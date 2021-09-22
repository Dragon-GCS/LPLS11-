from predict import *


if __name__ == '__main__':
    while True:
        try:
            teamA, teamB = input("请输入对战双方队伍名称，使用空格隔开, Q退出：\n").split()
            teamA_names, teamB_names, result = predict(teamA, teamB)
            print(f"红方：{teamA}\t蓝方：{teamB}")
            if result[0] > result[1]:
                print(f"蓝方 {teamB} 胜\n胜率：{result[0]:.2%}")
            else:
                print(f"红方 {teamA} 胜\n胜率：{result[1]:.2%}")
        except ValueError:
            exit()
        except SystemExit as e:
            print(e)