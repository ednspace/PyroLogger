#pragma once
#include <stdint.h>
#include <avr/pgmspace.h>

#include "Stream.h"
#include "Arduino.h"

namespace MLP
{
  class CommandParameter
  {
    // Buffer of parameters. As we work through each one, it gets null terminated. 
    char *m_pchBuffer;
    
    // Offset to next parameter in buffer. 
    uint8_t m_uNextParameter; 

  public:
    CommandParameter(char *pchBuffer, uint8_t nFirstParameter);
    const char *NextParameter();
  };
  
  struct CommandCallback 
  {
    const prog_char *m_strSensor;
    void (*m_Callback)(CommandParameter &rParameters);
  };

  template <int MAX_COMMANDS = 10, int CP_SERIAL_BUFFER_SIZE = 30> class CommandParser
  {
    // Array of commands we can match & dispatch. 
    CommandCallback m_Commands[MAX_COMMANDS];
    uint8_t m_uLastCommand;
    void (*m_DefaultHandler)();

    // Buffer for data received.
    char m_achBuffer[CP_SERIAL_BUFFER_SIZE];
    unsigned m_uNextCharacter; 
    bool m_bOverflow;
    const char m_chStartOfMessage, m_chEndOfMessage;

    // Source for commands to decode. 
    Stream &m_rSource;

  public:

    CommandParser(Stream &rSourceStream = Serial, char chStartOfMessage = '!', char chEndOfMessage = '\r')
      : m_chStartOfMessage(chStartOfMessage)
      , m_chEndOfMessage(chEndOfMessage)
      , m_rSource(rSourceStream)
    {
      Init();
      m_rSource = rSourceStream;
    }

    bool AddCommand(const __FlashStringHelper *pCommand, void(*CallbackFunction)(CommandParameter &rParameters))
    {
      if (m_uLastCommand < MAX_COMMANDS)
      {
        m_Commands[m_uLastCommand].m_Callback = CallbackFunction;
        m_Commands[m_uLastCommand].m_strSensor = (const prog_char*)pCommand;
        ++m_uLastCommand;
        return true;
      }
      return false; // too many commands stored already. 
    }

    void SetDefaultHandler(void(*CallbackFunction)())
    {
      m_DefaultHandler = CallbackFunction;
    }

    void Process()
    {
      while (Serial.available() > 0)
      {
        char chNext = m_rSource.read();
        if (chNext == m_chStartOfMessage)
        {
          Reset();
          m_achBuffer[0] = chNext; // the start character serves as a flag that this message is valid. 
          ++m_uNextCharacter;
        }
        else if (chNext == m_chEndOfMessage)
        {
          if (m_uNextCharacter > 0 && m_achBuffer[0] == m_chStartOfMessage && !m_bOverflow)
          {
            // We have a valid message. Dispatch it. 
            m_achBuffer[m_uNextCharacter] = '\0';
            DispatchMessage();
            Reset();
          }
        }
        else
        {
          // Store the character and advance the buffer. If there isn't enough
          // room for the message to be terminated by a null, flag overflow. 
          if (!m_bOverflow)
          {
            m_achBuffer[m_uNextCharacter++] = chNext;
            m_bOverflow = m_uNextCharacter >= (CP_SERIAL_BUFFER_SIZE - 1);
          }
        }
      }
    }

    void Reset()
    {
      m_uNextCharacter = 0;
      m_bOverflow = false;
    }

  private:
    void Init()
    {
      m_uLastCommand = 0; 
      m_DefaultHandler = NULL;

      m_bOverflow = false;
      m_uNextCharacter = 0;

    }

    void DispatchMessage()
    {
      uint8_t uCommand, uParameterStart;
      CommandCallback *pCommand;

      uCommand = m_uLastCommand;
      pCommand = m_Commands;
      while(uCommand--)
      {
        const prog_char *pchCommand = pCommand->m_strSensor;
        const char *pchTest = m_achBuffer + 1; // First element is start character.
        char chCommand, chTest;
        uParameterStart = 1;
        do 
        {
          chCommand = pgm_read_byte_near(pchCommand++);
          chTest = *pchTest++;
          ++uParameterStart;
        } while (chCommand == chTest && chCommand != '\0' && (chTest != ' ' || chTest != '\0'));

        if (chCommand == '\0' && (chTest == ' ' || chTest == '\0'))
        {
          CommandParameter Parameters(m_achBuffer, uParameterStart);
          pCommand->m_Callback(Parameters);
          return;
        }
        ++pCommand;
      }
      if (m_DefaultHandler != NULL)
        (*m_DefaultHandler)();
    }

  };
}
