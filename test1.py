import plotly.express as px
import plotly.graph_objects as go
import argparse
import re
import sys
import numpy as np

parser = argparse.ArgumentParser(description='Plots data from Aktyn and Pirania and Sipar')
parser.add_argument('fileName', metavar='F', nargs=1, help='Filename of PIR data')


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
  array = np.array(array)
  return array
  


def main():
  args = parser.parse_args()
  fileName = args.fileName[0]
  array = parseFile(fileName)
  #df = px.data.gapminder().query("country=='Canada'")
  #print(type(df))
  #fig = px.line(df, x="year", y="lifeExp", title='Life expectancy in Canada')
  
  x = array[:,0].tolist()
  
  fig = go.Figure(data=[go.Scattergl(x=x, y=x)], layout=go.Layout(title=go.layout.Title(text="A Bar Chart")))
  fig.show()




if __name__ == "__main__":
    # execute only if run as a script
    main()
