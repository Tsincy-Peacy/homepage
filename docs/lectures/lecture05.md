# 汇编语言第五讲

## 第十一章：标志寄存器

8086 的标志寄存器 `flag` 有 16 位，其中存储的信息通常被称为 PSW（Program Status Word）。其他寄存器是用来存放数据的，而 `flag` 按位存储信息的，每一位都有专门的含义：

- 0：CF，Carry Flag

- 2：PF，Parity Flag

- 4：AF，Auxiliary Carry Flag

- 6：ZF，Zero Flag

- 7：SF，Sign Flag

- 8：TF，Trap Flag

- 9：IF，Interrupt Enable Flag

- 10：DF，Direction Flag

- 11：OF，Overflow Flag

除了上述位，其他位没有意义。

### `ZF`

零标志位，记录相关指令执行后的结果是否为 0。如果为 0，`ZF` = 1；否则，`ZF` = 0。

分析以下代码：

```
mov ax, 1
sub ax, 1
```

执行后，`AX` = 0，`ZF` = 1。

在 8086 CPU 的指令集中，有的指令的执行是影响标志寄存器的，比如 `add`、`sub`、`mul`、`div`、`inc`、`or`、`and` 等，大多为运算指令；有的指令的执行对标志寄存器没有影响，比如 `mov`、`push`、`pop` 等，它们大多为传送指令。

### `PF`

奇偶标志位，记录相关指令执行后，其结果所有的 bit 位中 1 的个数是否为偶数。如果是则 `PF` = 1，否则 `PF` = 0。

分析以下代码：

```
mov al, 1
or al, 2
```

执行后，`AL` = 00000011b，`PF` = 1。

### `SF`

符号标志位，记录相关指令执行后，其结果是否为负。如果是则 `SF` = 1，否则 `SF` = 0。

分析以下代码：

```
mov al, 01111111b
add al, 1
```

执行后，`AL` = 10000000b，`SF` = 1。

### `CF`

进位标志位，记录相关指令执行后是否产生进位或借位。如果是则 `CF` = 1，否则 `CF` = 0。

分析以下代码：

```
mov al, 11111111b
add al, 1
```

执行后，`AL` = 00000000b，`CF` = 1。

分析以下代码：

```
mov al, 0
sub al, 1
```

执行后，`AL` = 11111111b，`CF` = 1。

### `OF`

溢出标志位，记录计算指令是否发生溢出。如：正 + 正 = 负。

注意区分 `CF` 和 `OF`，`CF` 考察的是虚拟的额外位，`OF` 考察的是实际的最高位。

分析以下代码：

```
mov al, 98
add al, 99
```

执行后，`AL` < 0，OF = 1。

### `adc`

指令格式：

`adc, obj1, obj2`

作用：

`obj1 = obj1 + obj2 + CF`

为什么要有这么一条指令呢？分析以下代码：

```
mov ax, 00ffh
mov bx, 1
add ax, bx

mov al, 0ffh
mov ah, 0
mov bx, 1
add al, bl
adc ah, bh
```

两段代码实现了相同的功能。拓展一下，16 位处理器处理 32 位数据的原理同上。

### `sbb`

指令格式：

`sbb obj1, obj2`

作用：

`obj1 = obj1 - obj2 - CF`

意义类似于 `adc`。

### `cmp`

指令格式：

`cmp obj1, obj2`

作用：

`ZF = obj1 == obj2`

`cmp` 指令实际上在做减法运算，只是没有保存结果。

### 条件转移指令

“条件”说的是根据某种条件决定是否跳转，比如 `jcxz` 就是根据 `CX` 是否为 0 来决定是否跳转。

下面是根据 `cmp` 指令的结果进行跳转的指令：

- `je`：等于

- `jne`：不等于

- `jb`：小于

- `jnb`：不小于

- `ja`：大于

- `jna`：不大于

这些指令的格式同 `jcxz`。

### `DF`

方向标志位，在传处理指令中，控制每次操作后 `SI`、`DI`的增减。

- `DF = 0`：每次操作后 `SI`、`DI` 递增。

- `DF = 1`：每次操作后 `SI`、`DI` 递减。

串传送指令：

`movsb`

功能：

```
byte ptr ES:[DI] = byte ptr DS:[SI]
inc DI | dec DI
inc SI | dec SI
```

`movsw`

功能：

```
word ptr ES:[DI] = word ptr DS:[SI]
add DI, 2 | sub DI, 2
add SI, 2 | sub SI, 2
```

以上指令和 `rep` 配合使用，功能为：

```
s:
    movsb
    loop s
```

8086 提供了修改 `DF` 的指令：

- `cld`：clear DF，将 `DF` 设置为 0

- `std`：set DF，将 `DF` 设置为 1

分析以下代码：

```
assume cs:code

data segment
    db 16 dup (0)
    db 16 dup (1)
data ends

code segment
    mov ax, data
    mov ds, ax
    mov si, 1fh
    mov ax, data
    mov es, ax
    mov di, 0fh
    mov cx, 16
    std
    rep movsb
code ends
```

### `pushf` 和 `popf`

`pushf` 的功能是将 `flag` 压栈，`popf` 是将 `flag` 弹栈。它们为访问标志寄存器提供了一种方法。

分析以下程序：

```
mov ax, 0
push ax
popf
mov ax, 0fff0h
add ax, 0010h
pushf
pop ax
and al, 11000101b
and ah, 00001000b
```

执行后，`AX` 的值是多少？

## 第十二章：内中断

首先解释一下什么是中断。当 CPU 在执行普通指令时，可能会出现意料之外的错误，如：执行除法时无法存放结果，这时 CPU 会中断指令的执行，跳到一段预先定义的特殊指令处执行相应的处理，这个过程就就叫中断。

分析以下代码：

```
mov ax, 0ffffh
mov dx, 1
div dx
```

单步运行，查看程序如何运行。

出现在 CPU 内部的异常被称为内中断，与之相对，来自于外部的异常被称为外中断。

当 CPU 内部发生如下情况时会产生内中断：

- `div` 溢出

- 单步执行

- 执行 `into` 指令

- 执行 `int` 指令

我们已经演示了 `div` 溢出的情形，现在着重讲解 `int` 指令。

`int` 指令已经在之前的程序中出现过：

```
mov ax, 4c00h
int 21h
```

这是程序的正常返回语句。

指令格式：

`int code`

作用：

执行编号为 `code` 的中断处理程序。作为初学者，我们先不用管如何编写中断处理程序，只需要在合适的时候调用合适的中断代码即可。

## 第十三章：`int` 指令

这一章主要讲解如何编写和安装中断处理程序，如上述所言，在深入学习之前可以跳过。

## 第十四章：端口

### 端口读写

部分外设通过端口与 CPU 进行通讯，对于这部分设备有一对特殊的指令与其通讯：

端口地址：0 ~ 255

- `in al, address`

- `out address, al`

端口地址：255 ~ 65535

- `mov dx, address`

- `in al, dx`

- `out dx, al`

简单了解即可。

### `shl` 和 `shr`

`shl` 是逻辑左移指令，`shr` 是逻辑右移指令。

指令格式：

```
shl al, 1

mov cl, idata
shl al, cl
```

作用：

将 `AL` 左移 1 位或 `CL` 位，末尾补 0，最高位被写入 `CF` 中。注意，`shl` 左移的位数大于 1 时只能放在 `CL` 中。

`shr` 与 `shl` 相反，右移 1 位或 `CL` 位，高位补 0，最低为被写入 `CF` 中。

