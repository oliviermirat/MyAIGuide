inputFile  = "ManicTimeData_2020-12-30App.csv"
outputFile = "blankScreenComputer.csv"

f = open(outputFile, "w+", encoding="utf8")
with open(inputFile, 'r', encoding="utf8") as reader:
  line = reader.readline()
  while line != '':
    line = reader.readline()
    if line[1:19] == 'Blank Screen Saver':
      f.write(line)
