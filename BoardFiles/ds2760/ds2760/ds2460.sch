v 20050313 1
T 73700 22300 9 10 1 0 0 0 1
DS2760 Based Thermocouple Sensor
T 73400 21700 9 10 1 0 0 0 1
ds2760.sch
T 73700 21400 9 10 1 0 0 0 1
1
T 75200 21400 9 10 1 0 0 0 1
1
T 77400 21700 9 10 1 0 0 0 1
1.00
T 77200 21400 9 10 1 0 0 0 1
Eric Daine
N 73100 26500 73100 25700 4
N 71100 26500 71100 25700 4
N 71100 26100 70200 26100 4
N 73100 26100 74200 26100 4
N 74200 24100 76700 24100 4
N 70200 26100 70200 23300 4
N 70200 23300 76700 23300 4
N 71100 24900 71100 24200 4
N 71100 24200 71900 24200 4
N 73100 24900 73300 24900 4
N 73300 24900 73300 24200 4
N 73300 24200 72400 24200 4
T 75400 23500 9 10 1 0 0 0 1
Thermo Negative
T 75400 24300 9 10 1 0 0 0 1
Thermo Positive
N 71100 25300 68400 25300 4
N 68400 25300 68400 28200 4
N 68400 28200 65500 28200 4
T 65300 27900 9 10 1 0 0 0 1
Data (DQ)
N 68600 29900 67900 29900 4
N 67900 29900 67900 28200 4
N 69800 29500 74200 29500 4
N 65500 29100 65500 31300 4
N 65500 31300 74200 31300 4
N 74200 24100 74200 31300 4
T 65200 28800 9 10 1 0 0 0 1
GND
N 71100 27300 73100 27300 4
N 72100 27300 72100 30300 4
N 69800 30300 73000 30300 4
N 73500 30300 74200 30300 4
N 73100 27700 73600 27700 4
N 73600 27700 73600 28100 4
N 73600 29000 72100 29000 4
C 64000 20900 0 0 0 title-bordered-B.sym
C 69800 29200 1 90 0 BAT54S.sym
{
T 68700 29400 5 10 1 1 90 0 1
refdes=D1
}
C 73700 28100 1 90 0 resistor-1.sym
{
T 73500 28600 5 10 1 1 180 0 1
refdes=R1
T 73700 28100 5 10 0 0 0 0 1
footprint=1206
T 73700 28100 5 10 1 1 0 0 1
value=1K
}
C 72500 24000 1 90 0 capacitor-0.sym
{
T 72000 24300 5 10 1 1 90 0 1
refdes=C2
T 72400 24300 5 10 1 1 90 0 1
value=0.1uF
T 72500 24000 5 10 0 0 90 0 1
footprint=1206
}
C 73600 30100 1 90 0 capacitor-0.sym
{
T 73100 30400 5 10 1 1 90 0 1
refdes=C1
T 73500 30400 5 10 1 1 90 0 1
value=0.1uF
T 73600 30100 5 10 0 0 90 0 1
footprint=1206
}
C 77600 24200 1 180 0 terminal-1.sym
{
T 77350 24150 5 10 1 1 180 6 1
refdes=T3
}
C 77600 23400 1 180 0 terminal-1.sym
{
T 77350 23350 5 10 1 1 180 6 1
refdes=T4
}
C 64600 29000 1 0 0 terminal-1.sym
{
T 64850 29050 5 10 1 1 0 6 1
refdes=T1
}
C 64600 28100 1 0 0 terminal-1.sym
{
T 64850 28150 5 10 1 1 0 6 1
refdes=T2
}
C 71100 24500 1 0 0 ds2760.sym
{
T 72800 28200 5 10 1 1 0 6 1
refdes=U1
T 71100 24500 5 10 0 0 0 0 1
footprint=DS2760
}
