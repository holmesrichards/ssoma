def main():
    vefc = [
        [[0,0,1,1], [0,1,1,0], [1,1,0,0]],
        [[0,1,1,1], [0,0,2,1], [0,1,2,0], [0,2,1,0], [1,2,0,0], [1,1,1,0]],
        [[0,1,2,1], [1,2,1,0]],
        [[0,2,2,1], [0,2,3,0], [2,3,0,0], [2,2,1,0]],
        [[0,3,2,1], [3,2,1,0]],
        [[0,3,3,1], [3,3,1,0]]
        ]

    pick = [0,0,0,0,0,0]
    
    while True:
        j = len(vefc)-1
        while pick[j] == len(vefc[j])-1:
            pick[j] = 0
            j -= 1
            if j < 0:
                break
        if j < 0:
            break
        pick[j] += 1
        sum = [0, 0, 0, 0]
        for j in range(len(vefc)):
            for i in range(len(sum)):
                sum[i] += vefc[j][pick[j]][i]
        if sum == [8, 12, 6, 1]:
            for j in range(len(vefc)):
                print (vefc[j][pick[j]], end=" ")
            print (sum)

main()
