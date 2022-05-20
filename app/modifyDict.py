def divDemand(cap_divid, x_divisor):
    cociente, resto = divmod(cap_divid, x_divisor)
   # print("Capacidad: {}, Cociente: {}, Resto: {}".format(cap_divid, cociente, resto))
   # print("Done!!!")
    return cociente, resto

def modifyDict(demands, x_divisor):
    # iterate dictionary getting key, value
    value = []
    for k, v in demands.items():
        c, r = divDemand(int(v), x_divisor)
        lc = [x_divisor for _ in range(c)]
        #lr = [1 for _ in range(r)]
        lr = [r]
        value = lc + lr

        if len(value) == 0:
            value = [0]

        demands[k] = value
    return demands



def bsort(lista):
    '''
    Sort a list of elements using bubble sort algorithm
    '''
    
    for _ in range(len(lista)):
        for j in range(len(lista)-1):
            if lista[j] > lista[j+1]:
                lista[j], lista[j+1] = lista[j+1], lista[j]
    return lista

if __name__ == '__main__':
    print(bsort([1,2,3,4,5,7,6,8,9,10]))