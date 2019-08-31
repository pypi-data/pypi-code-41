
import turtle
turtle.showturtle()
# 第一个环
turtle.penup()  # 抬笔，因为不画线
turtle.goto(-200, 0)
turtle.color("blue")
turtle.pendown() # 落笔，需要画线了，也就是圆圈
turtle.circle(50)

# 第二环
turtle.penup()
turtle.goto(-145, -50)
turtle.color("orange")
turtle.pendown()
turtle.circle(50)

# 第三环
turtle.penup()
turtle.goto(-95, 0)
turtle.color("black")
turtle.pendown()
turtle.circle(50)


# 第四环
turtle.penup()
turtle.goto(-40, -50)
turtle.color("green")
turtle.pendown()
turtle.circle(50)


# 第五环
turtle.penup()
turtle.goto(15, 0)
turtle.color("red")
turtle.pendown()
turtle.circle(50)

