#include "CommandParser.h"

using namespace MLP;

CommandParameter::CommandParameter(char *pchBuffer, uint8_t uFirstParameter)
{
  m_pchBuffer = pchBuffer;
  m_uNextParameter = uFirstParameter;
}

const char *CommandParameter::NextParameter()
{
  if (m_pchBuffer[m_uNextParameter] == '\0')
    return NULL;

  // Null terminate the next parameter
  char *pchParameter = m_pchBuffer + m_uNextParameter;
  char *pchEnd = pchParameter;
  while (*pchEnd != ' ' && *pchEnd != '\0')
  {
    ++pchEnd;
    ++m_uNextParameter;
  }

  if (*pchEnd != '\0')
  {
    ++m_uNextParameter;
    *pchEnd = '\0';
  }

  return pchParameter;
}