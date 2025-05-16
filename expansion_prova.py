def gen_listof_int(min: int, max: int, step: int) -> list[int]:
    return list(range(min, max, step))

def square_list(lista: list[int]) -> list[int]:
    return [num*num for num in lista]    
    

lista_numeri = gen_listof_int(1, 10, 1)
square_lista = square_list(lista_numeri)

if __name__ == "__main__":    
    primo,*_, ultimo = square_lista
    print(primo, ultimo)

