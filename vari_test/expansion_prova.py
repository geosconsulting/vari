def gen_list_of_int(min: int, max: int, step: int) -> list[int]:
    return list(range(min, max, step))

def square_list(lista: list[int]) -> list[int]:
    return [num*num for num in lista]    
    

if __name__ == "__main__":    
    
    number_list = gen_list_of_int(1, 10, 1)
    print(number_list)
    
    primo,*_, last_element = square_list(number_list)
    print(primo, last_element)

