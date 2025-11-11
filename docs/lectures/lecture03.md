# 汇编语言第三讲

## 第八章：数据处理的两个基本问题

所谓的两个问题：

1. 数据在什么地方？

2. 数据有多长？

定义两个符号：`reg` 和 `sreg`

- `reg`：表示寄存器，包括 `ax`、`bx`、`cs`、`dx`、`ah`、`al`、`bh`、`bl`、`ch`、`cl`、`dh`、`dl`、`sp`、`bp`、`si`、`di`。

- `sreg`：表示段寄存器，包括 `ds`、`ss`、`cs`、`es`。

### `bx`、`si`、`di` 和 `bp`

只有这四个寄存器可以出现在 `[...]` 中，且只能单个或以 `bx+si`、`bx+di`、`bp+si` 和 `bp+di` 的形式出现。

前三条寄存器默认段寄存器为 `ds`，而 `bp` 的默认段寄存器为 `ss`。

### `X ptr`

在有寄存器的情况下，数据长度由寄存器的长度给出，如 `ax` 是 16 位，`al` 是 8 位。但存在一些不涉及寄存器的操作，如 `mov [0], 1`，我们向 `[0]` 地址存入的是字还是字节？

为了明确这个问题，引入 `X ptr` 修饰符，加在地址单元之前，如 `mov word ptr [0], 1`，这样就明确存入的数据长度为 16，而 `mov byte ptr [0], 1` 则表示存入的数据长度为 8。

### 寻址方式练习

分析如下代码：

```
assume cs:code, ds:data

data segment
    dw 0, 0, 0, 0, 0, 0, 0, 0 ; ds:10h
    db 'DEC' ; 00
    db 'Ken Oslen' ; 03
    dw 137 ; 0C 
    dw 40 ; 0E
    db 'PDP' ; 10
data ends

code segment
s:
    mov dx, data
    mov ds, dx
    
    mov bx, 10h
    mov word ptr [bx+0ch], 38
    mov word ptr [bx+0eh], 70
    mov byte ptr [bx+10h+0h], 'V'
    mov byte ptr [bx+10h+1h], 'A'
    mov byte ptr [bx+10h+2h], 'X'
    
    mov ax, 4c00h
    int 21h
code ends

end s
```

### 新的指令

除法：

usage：`div reg/[...]`

该指令对于不同长度的操作数有不同的行为：

- 8 位：会将 `ax` 中的数除以操作数，并将商存入 `al` 中，将余数存入 `ah` 中。

- 16 位：会将 `dx|ax` 中的数除以操作数，并将商存入 `ax` 中，将余数存入 `dx` 中。

遗憾的是，这条指令在出现溢出时会进入中断处理。处理这种情况的方式将于后面给出。

存放双字：

usage: `dd idata`

我们之前见过 `db` 和 `dw`，分别存放 8 位 和 16 位数据，`dd` 则存放 32 位数据。

数据重复：

usage：`db idata dup (idata0, idata1, ...)`

这会将 `idata0, idata1, ...` 重复 `idata` 次。

## 第九章：转移指令的原理

可以修改 `IP`，或同时修改 `CS` 和 `IP` 的指令统称为转移指令。

### `offset`

还记得我们之前提到过的循环标记吗？事实上，它只是汇编语言代码段中偏移地址的一种标记，并不是只有循环才会用到。

在标记前面上 `offset` 关键字表示取回标号相对 `cs` 的偏移地址，分析如下代码：

```
assume cs:code

code segment
start:
    mov ax, offset start    ; 相当于 mov ax, 0
s:
    mov ax, offset s        ; 相当于 mov ax, 3
code ends
end start
```

由于 `mov ax, offset start` 翻译为机器码的长度为 24 位，所以在取 `s` 的偏移时为 3

分析如下代码：

```
assume cs:code

code segment
s:
    mov ax, bx
    mov si, offset s
    mov di, offset s0
    mov dx, cs:[si]
    mov cs:[di], dx
s0:
    nop
    mov ax, 4c00h
    int 21h
code ends
end s
```

### `jmp`

`jmp` 是无条件转移指令，其操作数可以是：

- `short s`：段内短转移，相对于当前指令的 -128 ~ 127，跳转到 `s` 所在的指令。

- `far ptr s`：段间长转移，同时修改 `CS` 和 `IP`，跳转到 `s` 所在的指令。

- `reg`：不再赘述。

- `word ptr [...]`：`IP` = `[...]`。

- `dword ptr [...]`：`CS` = `[...]`，`IP` = `[... + 2]`。

### `jcxz`

所有的有条件转移指令都是短转移，即转移范围为 -128 ~ 127。

usage：`jcxz s`

说明：这条指令表示如果 `CX` 为 0，则跳转至标号 `s` 处。

### `loop`

usage：`loop s`

先执行 `CX = CX - 1`，再判断是否 `CX ≠ 0`，若是则跳转至标号 `s` 处。

分析如下代码：

```
assume cs:code

code segment
start:
    mov ax, 2000h
    mov ds, ax
    mov bx, 0
s:
    mov cl, [bx]
    mov ch, 0
    inc cx
    inc bx
    loop s
ok:
    dec bx
    mov dx, bx
    mov ax, 4c00h
    int 21h
code ends
end start
```

### 控制显示屏

分析以下代码：
```
assume cs:code

code segment
    db 'H', 4, 'e', 4, 'l', 4, 'l', 4, 'o', 4, ',', 4, ' ', 4
    db 'w', 4, 'o', 4, 'r', 4, 'l', 4, 'd', 4, '!', 4
start:
    mov dx, 0B800h
    mov ds, dx
    
    mov bx, 0
    mov cx, 13
copy:
    mov dx, cs:[bx]
    mov [bx], dx
    add bx, 2
    loop copy
    
    mov ax, 4c00h
    int 21h
code ends
end start
```

8086 有一个 80 x 25 的彩色显示器，显示器可以显示 25 行，每行 80 个字符，每个字符有 256 种属性。

一个字符由其 ASCII 码和其属性（8 位）组成，即一个字。一行 80 个字符占 160 地址空间。

显示器的内存地址范围为 B8000H ~ BFFFFH，共 8000H 的地址空间，而显示器共有 8 页，即每页占用 1000H 的地址空间。显示器默认显示第一页。

属性字节的定义如下：

BL BR BG BB I FR FG FB

分别为：闪烁、背景红、背景绿、背景蓝、高亮、前景红、前景绿和前景蓝。
