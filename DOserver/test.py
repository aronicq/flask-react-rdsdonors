# import operator
#
# n = int(input())
# days = input().split(" ")
#
# dic = {k: int(v) for k, v in enumerate(days)}
# sort_dic=sorted(dic.items(), key=operator.itemgetter(1))
#
# c_min_time = n + 1
# for i in range(len(sort_dic)):
#     c_temp = sort_dic[i]
#     for j in range(1, 5):
#         if i + j > n - 1: continue
#
#         if abs(c_temp[1] - sort_dic[i + j][1]) <= 5 and c_min_time > abs(c_temp[0] - sort_dic[i + j][0]):
#             c_min_time = abs(c_temp[0] - sort_dic[i + j][0])
#
# if c_min_time == n + 1:
#     print("-1")
# else:
#     print(c_min_time - 1)
#
# n = int(input())
# array = input().split(" ")
# array = [int(i) for i in array]
#
# current_color = 1
# current_company = array[0]
# colors = [0] * len(array)
# colors[0] = current_color
# same_company_flag = 0
# companies = [0] * (max(array) + 1)
# companies[array[0]] = 1
#
# for i in range(1, len(array)):
#     if array[i] == array[i - 1]:
#         same_company_flag = 1
#     else:
#         same_company_flag = 0
#
#     if same_company_flag:
#         colors[i] = companies[array[i]]
#
#     else:
#         if companies[array[i]] == 0:
#             colors[i] = colors[i - 1] + 1
#         else:
#             colors[i] = companies[array[i]]
#
#     companies[array[i]] = colors[i]
#
#
# print(max(colors))
# print(*colors)

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "zdravstvuyte"

if __name__ == "__main__":
    app.run(debug = True, host="0.0.0.0", port = 5000)
