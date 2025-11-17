# 汇编语言第六讲

## 第十五章：外中断

外中断就是由外部设备产生的异常，需要 CPU 来执行特殊处理程序。键盘输入时就会产生外中断。

## 第十六章：直接定址表

### 描述单元长度的标号

分析以下程序：

```
assume cs:code

code segment
a:
    db 1, 2, 3, 4, 5, 6, 7, 8
b:
    dbw 0
start:
    mov si, offset a
    mov cx, 8
s:
    mov al, cs:[si]
    mov ah, 0
    add cs:[bx], ax
    inc si
    loop s

    mov ax, 4c00h
    int 21h
code ends
end start
```

上述程序中，`code`、`a`、`b`、`start`、`s` 都是标号，但是这些标号都指标是了内存单元的地址。

还有一种标号不但表示内存单元的地址，还表示了内存单元的长度，即在此标号处的是字节单元、字单元还是双字单元。其形式为：

`s db ...`

与常规标号相比，少了一个冒号。

于是，上述程序可以改写为：

```
assume cs:code

code segment
a
    db 1, 2, 3, 4, 5, 6, 7, 8
b
    dw 0
start:
    mov si, 0
s:
    mov al, a[si]
    mov ah, 0
    add b, ax
    inc si
    loop s
    mov ax, 4c00h
    int 21h
code ends
end start
```

代码是不是变得简介了一些？

### 在其他段中使用数据标号

一般来说，我们不在代码段定义数据，而是单独定义到其他段中。

注意，带“:”地址标号只能在代码段中使用，在其他段中使用无效。

将上述代码再次改写：

```
assume cs:code, ds:data

data segment
a
    db 1, 2, 3, 4, 5, 6, 7, 8
b
    dw 0
data ends

code segment
start:
    mov ax, data
    mov ds, ax

    mov si, 0
    mov cx, 8
s:
    mov al, a[si]
    mov ah, 0
    add b, ax
    inc si
    loop s

    mov ax, 4c00h
    int 21h
code ends
end start
```

注意，如果想在代码段中直接使用数据标号访问数据，必须使用伪指令 `assume` 将标号所在段和几个段寄存器联系起来，否则编译器无法确定段地址在哪个段寄存器中。

### 直接定址表

什么是直接定址表？简单来说，就是一个简单映射，分析以下代码：

```
data segment
    db '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'
data ends
```

如果给你 0 ~ 15 范围内随机一个数字，你能否将其对应的十六进制字符在显示器中显示出来？如果没有上述数据的定义，你需要判断给定的数字是否小于 10，然后将其转换为对应的字符，需要两套转换公式。但如果你已经有了上述数据的定义，你只需要在给定数字对应的内存单元处取得字符即可。这就是直接定址表的原理，使用预先定义的数据代替复杂的转换公式。

## 第十七章：使用 BIOS 进行键盘输入

分析以下程序：

```
assume cs:code

code segment
start:
    mov ax, 0B800h
    mov ds, ax
    
    mov cx, 13
    mov di, 0
s:
    mov ah, 0
    int 16h
    mov [di], al
    add di, 2
    loop s

    mov ax, 4c00h
    int 21h
code ends
end start
```

16h 号中断历程的 0 号服务是从输入缓冲区取回一个字符，`AH` 中存放状态码，`AL` 中存放 ASCII 码。
