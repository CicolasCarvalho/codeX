# codeX (alpha)

codeX é um programa para auxiliar o processo de criação de trabalhos para
diversas disciplinas

# Uso

Esse programa concatena todos os arquivos de uma dada pasta
afim de criar somente um com todos os exercicios resolvidos

## Exemplo:
```
trabalhos/
 ├─ fruber/
 │  ├─ 01122022_01.c
 │  ├─ 01122022_02.c
 ├─ codeX.py
```

`./fruber/01122022_01.c:`
```c
//@start include
//@once stdio
#include <stdio.h>
//@once math
#include <math.h>
//@end

int main(void) {
    //@start main
    printf("exercicio 1")
    //@end

    return 0;
}
```

`./fruber/01122022_02.c:`
```c
//@start include
//@once stdio
#include <stdio.h>
//@end

int main(void) {
    //@start main
    printf("exercicio 2")
    //@end

    return 0;
}
```

`trabalhos> ./codeX.py ./fruber`

`./fruber/out.c:`
```c
#include <stdio.h>
#include <math.h>

int main(void) {
    // 1)
    {
        printf("exercicio 1")
    }

    // 2)
    {
        printf("exercicio 2")
    }

    return 0;
}
```

# Decoradores

- @once - adiciona somente uma vez
- @ignore - ignora a linha abaixo
- @start - começa uma área (incl, defn, expl, expl-all, main, func)
- @end - finaliza a área

# Observações

_EU NÃO SEI PROGRAMAR EM PYTHON ESSE CÓDIGO PROVAVELMENTE POSSUI BUGS
    E MESMO SEM SABER EU SEI QUE ESTÁ TERRIVELMENTE MAL PROGRAMADO
    FIQUE À VONTADE PARA MUDAR E FAZER O QUE QUISER COM ELE_

*todos os arquivos devem serem finalizados com ..._xx.c*
