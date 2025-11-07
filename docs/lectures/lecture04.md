# 汇编语言第四讲

## 第十章：`CALL` 和 `RET` 指令

### `ret` 和 `retf`

- `ret` 相当于 `pop ip`

- `retf` 相当于 `pop ip, pop cs`

分析以下代码：

```
assume cs:code

stack segment
    db 16 dup (0)
stack ends

code segment
    mov ax, 4c00h
    int 21h
start:
    mov ax, stack
    mov ss, ax
    mov sp, 16
    mov ax, 0
    push ax
    ret
code ends
end start
```

- `ret` 指令将送入栈的 0 赋给 `IP`，使得程序跳转至 `code` 段的第一条指令。

分析以下代码：

```
assume cs:code

stack segment
    db 16 dup (0)
stack ends

code segment
    mov ax, 4c00h
    int 21h
start:
    mov ax, stack
    mov ss, ax
    mov sp, 16
    mov ax, 0
    push cs
    push ax
    retf
code ends
end start
```

- `retf` 将送入栈的 `CS` 和 `AX` 赋值给 `CS` 和 `SP`，跳转到了对应的指令处

### `call`

usage：

- `call s`

- `call far ptr s`

- `call reg`

- `call word ptr [...]`

- `call dword ptr [...]`

function：

- `push ip, jmp s`

- `push cs, push ip, jmp far ptr s`

- `push ip, jmp reg`

- `push ip, jmp word ptr [...]`

- `push cs, push ip, jmp dword ptr [...]`

分析以下代码：

```
    mov ax, 0
    call s
    inc ax
s:
    pop ax
```

- 执行代码后，`AX` 中的数值为多少？

分析以下代码：

```
    mov ax, 0
    call far ptr s
    inc ax
s:
    pop ax
    add ax, ax
    pop bx
    add ax, bx
```

- 执行代码后，`AX` 中的数值为多少？

只介绍前面两种用法，后面的不再赘述。下面我们来看一下 `call` 和 `ret` 的配合。

分析如下代码：

```
assume cs:code

code segment
start:
    mov ax, 1
    mov cx, 3
    call s
    mov bx, ax
    mov ax, 4c00h
    int 21h
s:
    add ax, ax
    loop s
    ret
code end
end start
```

程序结束后，`BX` 中的值是多少？

分析如下代码：

```
assume cs:code

stack segment
    db 8 dup (0)
    db 8 dup (0)
stack ends

code segment
start:
    mov ax, stack
    mov ss, ax
    mov sp, 16
    mov ax, 1000
    call s
    mov ax, 4c00h
    int 21h
s:
    add ax, ax
    ret
code ends
end start
```

观察栈的变化。

### `mul`

usage：

- `mul reg8`

- `mul reg16`

- `mul [...]`

function：

- `AX = AL x reg8`

- `DX|AX = AX x reg16`

- 不再赘述。

### 模块化程序设计

当我们将 `call` 和 `ret` 联合使用时，它像极了 C 语言中的函数调用，我们可以实现模块的独立封装。那么在这个过程中，如何处理参数和结果？

分析以下代码：

```
assume cs:code

data segment
    dw 1, 2, 3, 4, 5, 6, 7, 8
    dd 0, 0, 0, 0, 0, 0, 0, 0
data ends

code segment
start:
    mov ax, data
    mov ds, ax
    mov si, 0       ; ds:si 指向第一组 word 单元
    mov di, 16      ; ds:di 指向第二组 dword 单元

    mov cx, 8
s:
    mov bx, [si]
    call cube
    mov [di], ax
    mov [di+2], dx
    add si, 2       ; ds:si 指向下一组 word 单元
    add di, 4       ; ds:di 指向下一组 dword 单元
    loop s

    mov ax, 4c00h
    int 21h

cube:
    mov ax, bx
    mul bx
    mul bx
    ret
code ends
end start
```

请说明这段代码的作用。

### 批量数据的传递

当需要传递或返回多个数据时，寄存器数量是不够的，需要将数据存放在内存中，用寄存器记录其地址。

分析以下代码：

```
assume cs:code

data segment
    db 'conversation'
data ends

code segment
start:
    mov ax, data
    mov ds, ax
    mov si, 0
    mov cx, 12
    call captial
    mov ax, 4c00h
    int 21h
captial:
    and byte ptr [si], 11011111b
    inc si
    loop capital
    ret
code ends
end start
```

在这段程序中，我们使用 `SI` 和 `BX` 分别传递了字符串的地址和字符串的长度。

事实上，更加通用的传参做法是栈上传参，这将在以后提及。

### 寄存器冲突

分析以下程序：

```
assume cs:code

data segment
    db 'word', 0
    db 'unix', 0
    db 'wind', 0
    db 'good', 0
data ends

code segment
start:
    mov ax, data
    mov ds, ax
    mov bx, 0

    mov cx, 4
s:
    mov si, bx
    call capital
    add bx, 5
    loop s

    mov ax, 4c00h
    int 21h
captial:
    mov cl, [si]
    mov ch, 0
    jcxz ok
    and byte ptr [si], 11011111b
    inc si
    jmp short capital
ok:
    ret
code ends
end start
```

这个程序有一处致命错误，原程序和子程序是共用 `CX` 的，那么子程序对于 `CX` 的修改必然会影响到原程序的功能。如何解决？

我们只需要在子程序调用前加上 `push cx`、在子程序调用后加上 `pop cx`，即可消除子程序的影响。