# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
import igraph as ig

app = dash.Dash()

# Append an externally hosted CSS stylesheet
my_css_url = "https://codepen.io/chriddyp/pen/bWLwgP.css"
app.css.append_css({
    "external_url": my_css_url
})

# Append an externally hosted JS bundle
my_js_url = 'https://unkpg.com/some-npm-package.js'
app.scripts.append_script({
    "external_url": my_js_url
})

# app.css.config.serve_locally = True
# app.scripts.config.serve_locally = True

data = []

# 读取json文件放到data数组中

with open("E:/python_git/python/dash/useDash/json/res0.json","r") as f:
    data = json.loads(f.read())

L=len(data['links'])

nodes=[]

labels=[] # hovertext或者text显示的内容

Edges=[]

# 处理json文件函数，从源json文件生成nodes集合和labels集合的函数
def generate_lists(**kw):
    if kw['source'] not in labels:
        dict={}
        dict['name'] = kw['source']
        dict['group'] = kw['source_group']
        nodes.append(dict)
        labels.append(kw['source'])
    if kw['target'] not in labels:
        dict1={}
        dict1['name'] = kw['target']
        dict1['group'] = kw['target_group']
        nodes.append(dict1)
        labels.append(kw['target'])

# 处理json文件函数，生成edges集合的函数
def generate_edges(**kw):
    if kw['source'] in labels:
        i = labels.index(kw['source'])
    if kw['target'] in labels:
        j = labels.index(kw['target'])
    tup=(i, j)
    Edges.append(tup)

for k in range(L):
    generate_lists(**data['links'][k])
    generate_edges(**data['links'][k])

N=len(nodes)

G=ig.Graph(Edges, directed=False)

group=[] # group可以确定颜色分类，group中的值可以确定结点的size

for node in nodes:
    group.append(node['group'])

# 对group的值进行处理，使之更适于用在size表示上
l = len(group)

labels_text = [''] * l # 直接显示文字的list，用于非叶节点
labels_hover = [None] * l # 鼠标放上去才会显示的list，用于文字复杂的叶节点

sum_num = group[0] + group[l - 1]
for i in range(0, l):
    if group[i] == group[l-1]:
        labels_hover[i] = labels[i]
    else:
        labels_text[i] = labels[i]
    group[i] = sum_num - int(1.5 * group[i]) + 10

layt=G.layout('kk', dim=3)

Xn=[layt[k][0] for k in range(N)]# 节点的x坐标
Yn=[layt[k][1] for k in range(N)]# 节点的y坐标
Zn=[layt[k][2] for k in range(N)]# 节点的z坐标
Xe=[]
Ye=[]
Ze=[]
for e in Edges:
    Xe+=[layt[e[0]][0],layt[e[1]][0], None] # 边的x坐标
    Ye+=[layt[e[0]][1],layt[e[1]][1], None]
    Ze+=[layt[e[0]][2],layt[e[1]][2], None]

axis={
    'showbackground':False,
    'showline':False,
    'zeroline':False,
    'showgrid':False,
    'showticklabels':False,
    'title':''    # 标题，默认显示在坐标轴的终点
}

app.layout = html.Div([
    html.H1(
        'Memory Presentation',
        style = {
            'textAlign': 'center'
        }
    ),

    html.Div(
        '3D network graph',
        style = {
            'textAlign': 'center'
        }
    ),
    
    html.Div([
        html.Button(
            'prev',
            id = 'prev-button',
            style = {
                'float': 'left'
            }
        ),
        html.Button(
            'next',
            id = 'next-button',
            style = {
                'float': 'left'
            }
        )
    ],style={'height':40}),

    dcc.Graph(
        id = 'network-graph',
        figure = {
            'data':[
                go.Scatter3d(
                    x=Xe,
                    y=Ye,
                    z=Ze,
                    mode='lines',
                    line = {'width':1, 'color': 'rgb(125, 125, 125)'},    # 散点中间连接的线条是灰色，宽度是1px
                    hoverinfo='none'
                ),
                go.Scatter3d(
                    x=Xn,
                    y=Yn,
                    z=Zn,
                    mode='markers+text',    # marker属性是只显示散点，不显示它的说明文字，marker+text两者都显示，文字显示位置可用textposition控制
                    name='process',    # name会在鼠标悬停时显示在出现的框的外面的右边
                    marker = {
                        'size': group,    # 散点大小
                        'line': {'width':0.5, 'color': 'rgb(50,50,50)'},    # 线条是深灰色
                        'symbol': 'circle',    # 控制散点的形状，circle是圆形，circle-open是里面的不带颜色的
                        'color': group,    # 给散点颜色分类的，否则颜色都一样
                        'colorscale': 'Portland'   # 控制散点的色彩范围  
                    },
                    text=labels_text,    # 与每个坐标相关联的文本，如果设置了hoverinfo，且没设置hovertext时，这些文本会被显示；如果没设置hoverinfo，会直接接着显示在悬浮框里
                    hovertext = labels_hover,
                    hoverinfo='text' # 决定鼠标划过时显示什么信息，比如xy轴坐标等
                )
            ],
            'layout':go.Layout(
                width=1400,
                height=800,
                showlegend=False,    # 决定是否在右上角显示哪条线对应什么，哪个点对应什么，默认为true，
                scene={    # 设置此轨迹的3D坐标系和3D场景之间的引用
                    'xaxis': axis,
                    'yaxis': axis,
                    'zaxis': axis
                },
                margin = {'l' : 'auto', 'b' : 10, 't' : 10, 'r' : 'auto'},    # 控制Graph离网页边缘的距离
                hovermode='closest',    # 确定此场景的悬停交互模式，有两个值，一个是closest，一个是False，
                annotations = [{    # 注解，它是一个文本元素，可以放置在图形的任何地方，它可以根据图中的相对坐标或相对于图的实际数据坐标来定位，它可以显示为有或没有箭头
                    'showarrow':False,    # 确定注释是否用箭头绘制。如果true，文本放在箭头的尾部附近；如果False，text与提供的x和y对齐
                    'text':"res0.json",    # 设置与此注释关联的文本
                    'xref':'paper',    # 设置注释的x坐标轴
                    'yref':'paper',
                    'x':0,    # 设置注释的x位置
                    'y':0.1,
                    'xanchor':'left',    # 设置文本框的水平位置
                    'yanchor':'bottom',
                    'font':{'size':14}
                }]
            )
        }

    ),

    html.Pre(
        id = 'node-content',
        style = {
            'height': 200,
            'width': '90%',
            'marginLeft': 'auto',
            'marginRight': 'auto',
            'borderStyle':'solid',
            'borderColor':'black',
            'borderWidth':1 
        }
    )
])

if __name__ == '__main__':
    app.run_server()