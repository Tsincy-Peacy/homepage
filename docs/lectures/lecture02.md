# 汇编语言第二讲

## 第六章：包含多个段的程序

### 在代码段中使用数据

分析如下代码：

```
assume cs:code

code segment

    dw 0123h, 0456h, 0789, 0abch, 0defh, 0fedh, 0cbah, 0987h
start:
    mov bx, 0
    mov ax, 0
    mov cx, 8
s:
    add ax, cs:[bx]
    add bx, 2
    loop s

    mov ax, 4c00h
    int 21h

code ends

end start
```

- `dw` 即为 define word，意为定义字型数据。

- `start` ... `end start` 标明了程序的执行范围，这向编译器解释了不要从开头定义的数据开始执行。

### 在代码段中使用栈

分析如下代码：

```
assume cs:code

code segment

dw 0123h, 0456h, 0789h, 0abch, 0defh, 0fedh, 0cbah, 0987h
dw 0, 0, 0, 0, 0, 0, 0, 0

start:
    mov ax, cs
    mov ss, ax
    mov sp, 20h
    mov bx, 0
    mov cx, 8
s:
    push cs:[bx]
    add bx, 2
    loop s

    mov bx, 0
    mov cx, 8
s0:
    pop cs:[bx]
    add bx, 2
    loop s0

    mov ax, 4c00h
    int 21h

code ends

end start
```

- 对 `SS` 和 `SP` 的修改改变了 `push` 和 `pop` 的默认行为。

### 数据、代码、栈分段存放

分析如下代码：

```
assume cs:code, ds:data, ss:stack
data segment
    dw 0123h, 0456h, 0789h, 0abch, 0defh, 0fedh, 0cbah, 0987h
data ends

stack segment
    dw 0, 0, 0, 0, 0, 0, 0, 0
stack ends

code segment
start:
    mov ax, stack
    mov ss, ax
    mov sp, 10h

    mov ax, data
    mov ds, ax
    
    mov bx, 0

    mov cx, 8
s:
    push [bx]
    add bx, 2
    loop s

    mov bx, 0
s0:
    pop [bx]
    add bx, 2
    loop s0

    mov ax, 4c00h
    int 21h
code ends
end start
```

- 主要关注 `code`、`data` 和 `stack` 段的定义，以及对应在代码中的初始化处理。

- `code`、`data` 和 `stack` 是段地址，可以被视为一个数字被送入寄存器中。

## 第七章：更灵活的定位内存地址的方法

### `and` 和 `or`

- `and` 指令：按位与

- `or` 指令：按位或

`and al, 00111011b`：`AL` = `AL` & 00111011B

`or al, 00111011b`：`AL` = `AL` | 00111011B

### ASCII 码

在汇编程序中，用 '...' 的形式给出的数据是字符。

分析以下程序：

```
assume cs:code, ds:data
data segment
    db 'unix'
    db 'fork'
data ends

code segment
start:
    mov al, 'a'
    mov bl, 'b'
    mov ax, 4c00h
    int 21h
code ends
end start
```

- `db` 表示 define byte，因为字符的 ASCII 码是 8 位。你可以在内存中的 `data` 段查看他们的具体值。

下面给出一份大小写转换的代码：

```
assume cs:code, ds:data
data segment
    db 'BaSiC'
    db 'iNfOrMaTiOn'
data ends

code segment
start:
    mov ax, data
    mov ds, ax

    mov bx, 0

    mov cx, 5
s:
    mov al, [bx]
    and al, 11011111b
    mov [bx], al
    inc bx
    loop s

    mov cx, 11
s0:
    mov al, [bx]
    or al, 00100000b
    mov [bx], al
    inc bx
    loop s0

    mov ax, 4c00h
    int 21h
code ends
end start
```

- 这个程序实现了将第一个字符串大写、第二个字符串小写的功能。

- 将任意字母的第 5 位置 0 即为大写，置 0 即为小写。

### `[bx + idata]`

分析以下代码：

```
assume cs:code, ds:data
data segment
    db 'BaSiC'
    db 'MinIX'
data ends
code segment
start:
    mov ax, data
    mov ds, ax

    mov bx, 0

    mov cx, 5
s:
    mov al, [bx]
    and a1, 11011111b
    mov [bx], al
    mov al, [5+bx]
    or al, 00100000b
    mov [5+bx], al
    inc bx
    loop s
code ends
end start
```

### `SI` 和 `DI`

`SI` 是 Source Index 的缩写，`DI` 是 Destination Index 的缩写，它们和 `BX` 的作用相似。

分析以下代码：

```
assume cs:code, ds:data
data segment
    db 'welcome to masm!'
    db '................'
data ends

code segment
start:
    mov ax, data
    mov ds, ax
    mov si, 0
    mov di, 16

    mov cx, 8
s:
    mov ax, [si]
    mov [di], ax
    add si, 2
    add di, 2
    loop s

    mov ax, 4c00h
    int 21h
code ends
end start
```

### `[bx+si+idata]` 和 `[bx+di+idata]`

以下指令是等效的：

- `mov ax, [bx+si+200]`

- `mov ax, [bx+200+si]`

- `mov ax, [200+bx+si]`

- `mov ax, 200[bx][si]`

- `mov ax, [bx].200[si]`

- `mov ax, [bx][si].200`
