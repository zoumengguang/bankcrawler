import csv

# Open and read files
with open('../data/productionBankList.csv'
    , 'r') as r1, open('../linksExtract.csv', 'r') as r2:
    sheet1 = r1.readlines()
    sheet2 = r2.readlines()
r1.close()
r2.close()

# Generate csv
with open('diff.csv', 'w') as out:
    out.write('Bank Name,Link Type' + '\n')
    for row in sheet1:
        arr = row.split(',')
        for row2 in sheet2[1::]:
            arr2 = row2.split(',')
            linkType = 'Production' if 'Production' in arr2[3] else 'Alpha'
            if arr[1] in row2.split(','):
                out.write(arr[1] + ',' + linkType + '\n')
