import numpy as np

# 打印迷宫
def print_maze(maze):
    for row in maze:
        for item in row:
            print(item, end='')
        print()

# 使用深度优先搜索解决迷宫问题
def path_finder_v1(maze, start, end, collision_block_char, verbose=False): 
    # 准备迷宫：标记起点和终点
    def prepare_maze(maze, start, end):
        maze[start[0]][start[1]] = "S"
        maze[end[0]][end[1]] = "E"
        return maze

    # 找到起点的位置
    def find_start(maze):
        for row in range(len(maze)):
            for col in range(len(maze[0])):
                if maze[row][col] == 'S':
                    return row, col

    # 检查位置是否有效
    def is_valid_position(maze, pos_r, pos_c):
        if pos_r < 0 or pos_c < 0:
            return False
        if pos_r >= len(maze) or pos_c >= len(maze[0]):
            return False
        if maze[pos_r][pos_c] in ' E':
            return True
        return False

    # 解决迷宫
    def solve_maze(maze, start, verbose=False):
        path = []
        stack = []  # 使用栈来进行深度优先搜索
        stack.append(start)  # 将起点添加到栈中
        while len(stack) > 0:  # 当栈中有元素时循环
            pos_r, pos_c = stack.pop()  # 弹出栈顶元素
            if verbose: 
                print("当前位置", pos_r, pos_c)
            if maze[pos_r][pos_c] == 'E':
                path += [(pos_r, pos_c)]
                return path
            if maze[pos_r][pos_c] == 'X':
                # 已经访问过的位置
                continue
            maze[pos_r][pos_c] = 'X'  # 标记当前位置为已访问
            path += [(pos_r, pos_c)]  # 记录路径
            # 检查所有可能的位置并添加到栈中
            if is_valid_position(maze, pos_r - 1, pos_c):
                stack.append((pos_r - 1, pos_c))
            if is_valid_position(maze, pos_r + 1, pos_c):
                stack.append((pos_r + 1, pos_c))
            if is_valid_position(maze, pos_r, pos_c - 1):
                stack.append((pos_r, pos_c - 1))
            if is_valid_position(maze, pos_r, pos_c + 1):
                stack.append((pos_r, pos_c + 1))
            if verbose: 
                print('栈:', stack)
                print_maze(maze)

        # 未找到路径
        return False

    # 清理迷宫，将碰撞块字符替换为障碍物标志
    new_maze = []
    for row in maze: 
        new_row = []
        for j in row: 
            if j == collision_block_char: 
                new_row += ["#"]
            else: 
                new_row += [" "]
        new_maze += [new_row]
    maze = new_maze

    maze = prepare_maze(maze, start, end)
    start = find_start(maze)
    path = solve_maze(maze, start, verbose)
    return path

# 使用广度优先搜索解决迷宫问题
def path_finder_v2(a, start, end, collision_block_char, verbose=False):
    # 进行一步移动
    def make_step(m, k):
        for i in range(len(m)):
            for j in range(len(m[i])):
                if m[i][j] == k:
                    if i > 0 and m[i - 1][j] == 0 and a[i - 1][j] == 0:
                        m[i - 1][j] = k + 1
                    if j > 0 and m[i][j - 1] == 0 and a[i][j - 1] == 0:
                        m[i][j - 1] = k + 1
                    if i < len(m) - 1 and m[i + 1][j] == 0 and a[i + 1][j] == 0:
                        m[i + 1][j] = k + 1
                    if j < len(m[i]) - 1 and m[i][j + 1] == 0 and a[i][j + 1] == 0:
                        m[i][j + 1] = k + 1

    # 清理迷宫，将碰撞块字符替换为障碍物标志
    new_maze = []
    for row in a: 
        new_row = []
        for j in row:
            if j == collision_block_char: 
                new_row += [1]
            else: 
                new_row += [0]
        new_maze += [new_row]
    a = new_maze

    m = []
    for i in range(len(a)):
        m.append([])
        for j in range(len(a[i])):
            m[-1].append(0)
    i, j = start
    m[i][j] = 1 

    k = 0
    except_handle = 150
    while m[end[0]][end[1]] == 0:
        k += 1
        make_step(m, k)
        if except_handle == 0: 
            break
        except_handle -= 1 

    i, j = end
    k = m[i][j]
    the_path = [(i,j)]
    while k > 1:
        if i > 0 and m[i - 1][j] == k-1:
            i, j = i-1, j
            the_path.append((i, j))
            k -= 1
        elif j > 0 and m[i][j - 1] == k-1:
            i, j = i, j-1
            the_path.append((i, j))
            k -= 1
        elif i < len(m) - 1 and m[i + 1][j] == k-1:
            i, j = i+1, j
            the_path.append((i, j))
            k -= 1
        elif j < len(m[i]) - 1 and m[i][j + 1] == k-1:
            i, j = i, j+1
            the_path.append((i, j))
            k -= 1
        
    the_path.reverse()
    return the_path

# 找到最近的坐标
def closest_coordinate(curr_coordinate, target_coordinates): 
    min_dist = None
    closest_coordinate = None
    for coordinate in target_coordinates: 
        a = np.array(coordinate)
        b = np.array(curr_coordinate)
        dist = abs(np.linalg.norm(a-b))
        if not closest_coordinate: 
            min_dist = dist
            closest_coordinate = coordinate
        else: 
            if min_dist > dist: 
                min_dist = dist
                closest_coordinate = coordinate

    return closest_coordinate

# 找到路径并返回
def path_finder(maze, start, end, collision_block_char, verbose=False):
    # 紧急修补：修复起点和终点的坐标
    start = (start[1], start[0])
    end = (end[1], end[0])
    # 紧急修补结束

    path = path_finder_v2(maze, start, end, collision_block_char, verbose)

    new_path = []
    for i in path: 
        new_path += [(i[1], i[0])]
    path = new_path
    
    return path

# 找到最优路径
def path_finder_2(maze, start, end, collision_block_char, verbose=False):
    start = list(start)
    end = list(end)

    t_top = (end[0], end[1]+1)
    t_bottom = (end[0], end[1]-1)
    t_left = (end[0]-1, end[1])
    t_right = (end[0]+1, end[1])
    pot_target_coordinates = [t_top, t_bottom, t_left, t_right]

    maze_width = len(maze[0]) 
    maze_height = len(maze)
    target_coordinates = []
    for coordinate in pot_target_coordinates: 
        if coordinate[0] >= 0 and coordinate[0] < maze_width and coordinate[1] >= 0 and coordinate[1] < maze_height: 
            target_coordinates += [coordinate]

    target_coordinate = closest_coordinate(start, target_coordinates)

    path = path_finder(maze, start, target_coordinate, collision_block_char, verbose=False)
    return path

# 分别找到A和B的路径
def path_finder_3(maze, start, end, collision_block_char, verbose=False):
    curr_path = path_finder(maze, start, end, collision_block_char, verbose=False)
    if len(curr_path) <= 2: 
        return []
    else: 
        a_path = curr_path[:int(len(curr_path)/2)]
        b_path = curr_path[int(len(curr_path)/2)-1:]
    b_path.reverse()

    print (a_path)
    print (b_path)
    return a_path, b_path

if __name__ == '__main__':
    maze = [['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'], 
            [' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#'], 
            ['#', ' ', '#', ' ', ' ', '#', '#', ' ', ' ', ' ', '#', ' ', '#'], 
            ['#', ' ', '#', ' ', ' ', '#', '#', ' ', '#', ' ', '#', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#'], 
            ['#', '#', '#', ' ', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' '], 
            ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']]
    start = (0, 1)
    end = (0, 1)
    print (path_finder(maze, start, end, "#"))

    print ("-===")
    start = (0, 1)
    end = (11, 4)
    print (path_finder_2(maze, start, end, "#"))

    print ("-===")
    start = (0, 1)
    end = (12, 6)
    print (path_finder_3(maze, start, end, "#"))

    print ("-===")
    path_finder_3(maze, start, end, "#")[0]
    path_finder_3(maze, start, end, "#")[1]