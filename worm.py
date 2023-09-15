import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import os
from tkinter.ttk import Progressbar
import time


#存储路径
savePath = "C:\\Users\\86182\\Desktop\\洛谷习题\\"
#网址
turl = "https://www.luogu.com.cn/problem/list"
purl = "https://www.luogu.com.cn/problem/P"
midurl = "https://www.luogu.com.cn/problem/solution/P"
surl = "https://www.luogu.com.cn/blog/_post/"


#一般的获取html函数
def get_html(url):
   # 模拟用户使用浏览器访问
   headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.1.4031 SLBChan/103",
      "cookie": "__client_id=af4215a6f73e4641a2ae5ed49f35ef0b93b0709b; login_referer=https%3A%2F%2Fwww.luogu.com.cn%2Fauth%2Flogin; _uid=664601; C3VK=a66952"
   }
   response = requests.get(url=url, headers=headers)
   return response.text


#将难度编码进行转换
def dif_turn(dif):
   if dif == "1":
      d = "入门"
   elif dif == "2":
      d = "普及-"
   elif dif == "3":
      d = "普及&提高-"
   elif dif == "4":
      d = "普及+&提高"
   elif dif == "5":
      d = "提高+&省选-"
   elif dif == "6":
      d = "省选&NOI-"
   else:
      d = "NOI&NOI+&CTSC"
   return d

#生成文件夹
def born_portfolio(name):
   if not os.path.exists(name):
      os.mkdir(name)
   else:
      print("Portfolio already exists")

#获取题目关键词
def slice(t_list, key_list):
   if t_list[0] == "[":
      key_list.append(t_list[1:5] + t_list[10:13])
      key_list.append(t_list[5:9])


#获取存有题目的列表
def get_titles(url, t_list):
   thtml = get_html(url)
   soup = BeautifulSoup(thtml, "html.parser")
   all_titles = soup.findAll("li")
   for title in all_titles:
      name = title.find("a")
      t_list.append(name.string)


#获取题目的网页信息
def get_pHTML(url):
   phtml = get_html(url)
   return phtml


#获取题解的页面信息
def get_sHTML(url):
   shtml = get_html(url)
   key = get_postfix(shtml)
   new_url = surl + key
   new_shtml = get_html(new_url)
   return new_shtml


#将题目网页内容转化为md格式
def get_pMD(html):
   bs = BeautifulSoup(html, "html.parser")
   core = bs.select("article")[0]
   md = str(core)
   md = re.sub("<h1>", "# ", md)
   md = re.sub("<h2>", "## ", md)
   md = re.sub("<h3>", "#### ", md)
   md = re.sub("</?[a-zA-Z]+[^<>]*>", "", md)
   return md


#获取题解博客的后缀
def get_postfix(text):
   pattern = r"%22id%22%3A(\d+)"
   match = re.search(pattern, text)
   if match:
      return match.group(1)
   return None


#获取题目难度编码
def get_dif(url):
   thtml = get_html(url)
   text = urllib.parse.unquote(thtml)
   pattern = r'"difficulty":(\d)'
   numbers = re.findall(pattern, text)
   return numbers


#将题解网页内容转化为md格式
def get_sMD(html):
   bs = BeautifulSoup(html, "html.parser")
   core = bs.findAll("div", attrs={"id": "article-content"})
   md = str(core)
   md = re.sub("<h1>", "# ", md)
   md = re.sub("<h2>", "## ", md)
   md = re.sub("<h3>", "#### ", md)
   md = re.sub("</p>", "<br>", md)
   return md

#将md文件存下
def saveData(data, filename):
   file = open(filename, "w", encoding="utf-8")
   for d in data:
      file.writelines(d)
   file.close()


#爬取函数
def worm():
    #相应筛选按钮的函数
    def apply_filter():
        progress_bar["maximum"] = 100
        progress = 0    #设置进度范围
        filter_value1 = combo1.get()    #条件：题目难度
        filter_value2 = search_entry.get()  #关键词：如题目编号
        filter_value3 = combo3.get()    #条件：题目年份
        output_text.insert(tk.END, "您选择的筛选条件为: "+ filter_value1 + " " + filter_value2 + " " + filter_value3 + "\n")
        output_text.update()
        output_text.insert(tk.END, "正在缓慢爬取中，请耐心等待..." + "\n")
        output_text.update()

        num = []    #将符合的题目编号存入这个数组中
        t_list = []    #存放题目名
        dif_list = []    #存放难度编码
        get_titles(turl, t_list)
        dif_list = get_dif(turl)
        for i in range(1000, 1050):    #开始筛选符合条件的题目编号
            key_list = []    #存放题目的关键词信息（来源和题目编号）
            slice(t_list[i - 1000], key_list)
            dif = dif_turn(dif_list[i - 1000])
            dif = re.sub(r'&', '/', dif)    #将难度名进行转换便于之后的匹配
            #第一个条件匹配
            if (filter_value1 == dif) | (filter_value1 == "暂无评定"):
                t1 = 1
            else:
                t1 = 0
            #第二个条件匹配
            if filter_value2:
                if (filter_value2 != "P" + str(i)) & (filter_value2 != "请输入关键词"):
                    t2 = 0
                else:
                    t2 = 1
            else:
                t2 = 1
            #第三个条件匹配
            if filter_value3 != "题目年份":
                if key_list:
                    if key_list[1] == filter_value3:
                        t3 = 1
                    else:
                        t3 = 0
                else:
                    t3 = 0
            else:
                t3 = 1
            if t1 & t2 & t3:
                num.append(i)
        if num:
            increment = 100 / len(num)     #确定进度条增量
            for i in num:    #开始爬取
                output_text.insert(tk.END, "正在爬取P" + str(i) + "...")
                output_text.update()
                output_text.see(tk.END)    #实时更新爬取内容到界面
                key_list = []
                slice(t_list[i - 1000], key_list)
                dif = dif_turn(dif_list[i - 1000])
                phtml = get_pHTML(purl + str(i))
                shtml = get_sHTML(midurl + str(i))
                if phtml == "error":
                    output_text.insert(tk.END, "爬取失败，可能是不存在该题或无权查看" + "\n")
                    output_text.update()
                    output_text.see(tk.END)
                else:
                    problem = get_pMD(phtml)
                    solution = get_sMD(shtml)
                    output_text.insert(tk.END, "爬取成功！正在保存..." + "\n")
                    output_text.update()
                    output_text.see(tk.END)
                    if key_list:
                        born_portfolio(savePath + dif + "-" + key_list[0] + "-" + key_list[1])    #生成难度-来源-年份文件夹
                        path = savePath + dif + "-" + key_list[0] + "-" + key_list[1] + "\\"     #定义路径到该文件夹下
                    else:
                        born_portfolio(savePath + dif)
                        path = savePath + dif + "\\"
                    born_portfolio(path + "P" + str(i) + "--" + t_list[i - 1000])    #生成存放题目和题解的文件夹
                    new_path = path + "P" + str(i) + "--" + t_list[i - 1000] + "\\"    #定义路径到该文件夹下
                    saveData(problem, new_path + "P" + str(i) + "--" + t_list[i - 1000] + ".md")
                    saveData(solution, new_path + "P" + str(i) + "--" + t_list[i - 1000] + "题解" + ".md")
                    output_text.insert(tk.END, "保存成功!" + "\n")
                    output_text.update()
                    output_text.see(tk.END)
                    progress += increment
                    progress_bar["value"] = progress    #爬取成功，进度条增加
                    progress_label["text"] = f"Progress: {progress}%"
                    window.update()
            output_text.insert(tk.END, "爬取完毕..." + "\n")
            output_text.update()
            output_text.see(tk.END)
        else:
            output_text.insert(tk.END, "没有找到指定的题目哦...请再试一试其他条件" + "\n")
            output_text.update()
            output_text.see(tk.END)


    # 创建主窗口
    window = tk.Tk()
    window.title("爬取--洛谷习题")

    # 设置窗口大小和颜色
    window.geometry("600x300")  # 设置宽度为400像素，高度为300像素
    window.configure(bg="pink")

    # 创建标签和下拉菜单
    label1 = tk.Label(window, text="筛选条件:")
    label1.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    combo1 = ttk.Combobox(window, values=["暂无评定", "入门", "普及-", "普及/提高-", "普及+/提高", "提高+/省选-", "省选/NOI-", "NOI/NOI+/CTSC"])
    combo1.grid(row=0, column=1, padx=10, pady=10, sticky='w')

    #创建关键词搜索框
    def on_entry_click(event):
        if search_entry.get() == '请输入关键词':
            search_entry.delete(0, tk.END)
            search_entry.config(foreground='black')

    def on_focus_out(event):
        if search_entry.get() == '':
            search_entry.insert(0, '请输入关键词')
            search_entry.config(foreground='gray')

    search_entry = tk.Entry(window, width=15)
    search_entry.insert(0, '请输入关键词')
    search_entry.config(foreground='gray')
    search_entry.bind('<FocusIn>', on_entry_click)
    search_entry.bind('<FocusOut>', on_focus_out)
    search_entry.grid(row=0, column=2, padx=10, pady=10, sticky='w')

    #题目年份筛选框
    combo3 = ttk.Combobox(window, values=["题目年份", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011"])
    combo3.grid(row=0, column=3, padx=10, pady=10, sticky='w')


    #制作显示的进度条
    progress_label = tk.Label(window, text="Progress: 0%")
    progress_label.grid(row=1, column=0, columnspan = 2, padx=10, pady=10, sticky = 'w')

    progress_bar = Progressbar(window, orient=tk.HORIZONTAL, length=150, mode='determinate')
    progress_bar.grid(row=1, column=1, padx=10, pady=10)

    # 设置第1列的权重为1，以确保它能够适应标签的值变化
    window.grid_columnconfigure(0, weight=1)

    # 设置下拉菜单默认选择项
    combo1.current(0)
    combo3.current(0)

    # 创建按钮
    button = tk.Button(window, text="筛选", command=apply_filter)
    button.grid(row=1, column=3, padx=10, pady=10, sticky='e')

    # 创建文本框
    output_text = tk.Text(window, height=10, width=55)
    output_text.grid(row=2, column=0, rowspan=3,columnspan=10, padx=10, pady=10, sticky='w')

    # 启动主循环
    window.mainloop()


def main():
    # 创建主窗口
    window = tk.Tk()
    window.title("开始界面")
    # 设置窗口大小和颜色
    window.geometry("400x300")  # 设置宽度为400像素，高度为300像素
    window.configure(bg="pink")
    # 创建按钮,进入爬取界面
    button = tk.Button(window, text="开始爬取", command=worm, width=15, height=5)
    button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    # 启动主循环
    window.mainloop()

if __name__ == '__main__':
   main()

