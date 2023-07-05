import csv

mylist = [1, 2, 3, 4, 5]

with open('eggs.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',')
    spamwriter.writerow(['Spam'] + mylist)


myotherlist = []
print(myotherlist)

myotherlist = [1, 2, 3]
print(myotherlist)