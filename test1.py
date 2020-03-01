import plotly.express as px
import plotly.graph_objects as go
import argparse
import re
import sys
import os
import numpy as np
import pandas

parser = argparse.ArgumentParser(description='Plots data from Aktyn and Pirania and Sipar')
parser.add_argument('fileName', metavar='F', nargs=1, help='Filename of PIR data')
parser.add_argument('--dev', help='aktyn or sipar', required=False)


def parseFile(fileName):
  try:
    f = open(fileName, 'r')
  except OSError:
    print("File {} not found. Exiting".format(fileName))
    sys.exit(1)
  lines = f.readlines()
  # remove whitespace characters like `\n` at the end of each line
  lines = [x.strip() for x in lines]
  # fast forward to actual lines
  columns = re.compile('Column:.*')
  lineNum = 0
  for line in lines:
    if columns.match(line):
      #print("Match: {}".format(line))
      break
    else:
      lineNum = lineNum + 1

  # Remove word "Column:  " from the column list
  column = re.compile('Column:\W+')
  lines[lineNum] = column.split(line)[1]

  # Process column names until data is found
  dataLine = re.compile('(-?[0-9.]+\s*)+')
  columnDescriptors = []
  for i in range(lineNum, lineNum+50):
    if dataLine.fullmatch(lines[i]):
      break
    else:
      lineNum = lineNum + 1
      if (len(lines[i]) > 0):
        columnDescriptors.append(lines[i])
        
  # read data lines
  dataLines = lines[lineNum:]
  numbers = re.compile('\s+')
  array = []
  for dataLine in dataLines:
    if len(dataLine) == 0:   # skip empty lines
      continue
    numbersTxt = numbers.split(dataLine)
    values = list(map(float, numbersTxt))
    array.append(values)
  
  # convert to Pandas dataframe for display
  array = np.array(array)
  array = pandas.DataFrame(data=array, columns=columnDescriptors)
  return array
  


def main():
  args = parser.parse_args()
  fileName = args.fileName[0]
  array = parseFile(fileName)
  
  # excluded list contains columns to skip when displaying
  excludedList = ['1 - time [h]']
  if args.dev == None:
    if len(array.columns) > 10:
      toExclude = "aktyn"
    else:
      toExclude = "sipar"
  else:
    toExclude = args.dev
    
  if toExclude == "sipar":
    [excludedList.append(x) for x in ['6 - latitude +/N -/S', 
                                      '7 - longitude +/E -/W']]
  elif toExclude == "aktyn":
    [excludedList.append(x) for x in ['6 - latitude +/N -/S', 
                                      '7 - longitude +/E -/W',
                                      '11 - temperature Water (deg. C)',
                                      '12 - Raw Pyranometer Upper (V)',
                                      '13 - Raw Pyranometer IR Upper (V)',
                                      '14 - Raw Pyranometer IR Lower (V)',
                                      '15 - Raw Pyranometer Lower (V)',
                                      '16 - Raw Thermometer Pyranometer IR Upper (V)',
                                      '17 - Raw Thermometer Pyranometer IR Lower (V)',
                                      '18 - Raw Thermometer Air (V)',
                                      '19 - Raw Thermometer Water (V)']]
  else:
    print("Error! Unknown device")
    sys.exit(-1)
  
  # hours are repeated for all columns
  hours = array['1 - time [h]'].to_numpy()
  
  # construct a Figure with lines + markers
  fig = go.Figure()
  
  for col in array.columns:
    if col in excludedList:
      continue
    fig.add_trace(go.Scatter(x=hours, y=array[col].to_numpy(),
                      mode='lines',
                      name=col))
    
  latTable = array['6 - latitude +/N -/S'].to_numpy()
  y = latTable.item(int(latTable.size/2))
  lonTable = array['7 - longitude +/E -/W'].to_numpy()
  x = lonTable.item(int(lonTable.size/2))
  fig.update_layout(
        title = 'File: {} ({},lat:{},lon:{})'.format(os.path.basename(args.fileName[0]),toExclude,y,x),
        xaxis = dict(range=[0,24]),
        )
  fig.update_xaxes(nticks=24)

  fig.show()  
  # now we are done
  sys.exit(0)



if __name__ == "__main__":
    # execute only if run as a script
    main()
