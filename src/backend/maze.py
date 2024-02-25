import json
import math
from opensource.generative_agent_simple.backend.global_methods import *
from utils import *

class Maze:
    def __init__(self, maze_name):
        self.maze_name = maze_name
        # 加载迷宫元信息
        meta_info = json.load(open(f"{env_matrix}/maze_meta_info.json"))
        self.maze_width = int(meta_info["maze_width"])
        self.maze_height = int(meta_info["maze_height"])
        self.sq_tile_size = int(meta_info["sq_tile_size"])
        self.special_constraint = meta_info["special_constraint"]
        blocks_folder = f"{env_matrix}/special_blocks"

        # 读取不同类型方块的信息
        wb = read_blocks_info(blocks_folder + "/world_blocks.csv")
        sb_dict = read_blocks_info_as_dict(blocks_folder + "/sector_blocks.csv")
        ab_dict = read_blocks_info_as_dict(blocks_folder + "/arena_blocks.csv")
        gob_dict = read_blocks_info_as_dict(blocks_folder + "/game_object_blocks.csv")
        slb_dict = read_blocks_info_as_dict(blocks_folder + "/spawning_location_blocks.csv")
        maze_folder = f"{env_matrix}/maze"

        # 读取迷宫地图信息
        collision_maze_raw = read_file_to_list(maze_folder + "/collision_maze.csv", header=False)[0]
        sector_maze_raw = read_file_to_list(maze_folder + "/sector_maze.csv", header=False)[0]
        arena_maze_raw = read_file_to_list(maze_folder + "/arena_maze.csv", header=False)[0]
        game_object_maze_raw = read_file_to_list(maze_folder + "/game_object_maze.csv", header=False)[0]
        spawning_location_maze_raw = read_file_to_list(maze_folder + "/spawning_location_maze.csv", header=False)[0]

        self.collision_maze = self.parse_maze(collision_maze_raw, meta_info["maze_width"])
        sector_maze = self.parse_maze(sector_maze_raw, meta_info["maze_width"])
        arena_maze = self.parse_maze(arena_maze_raw, meta_info["maze_width"])
        game_object_maze = self.parse_maze(game_object_maze_raw, meta_info["maze_width"])
        spawning_location_maze = self.parse_maze(spawning_location_maze_raw, meta_info["maze_width"])

        self.tiles = []
        for i in range(self.maze_height):
            row = []
            for j in range(self.maze_width):
                tile_details = self.create_tile_details(wb, sb_dict, ab_dict, gob_dict, slb_dict, i, j, sector_maze,
                                                        arena_maze, game_object_maze, spawning_location_maze)
                row.append(tile_details)
            self.tiles.append(row)

        # 为方块添加事件
        self.add_tile_events()

        # 地址和方块的映射
        self.address_tiles = self.map_address_to_tiles()

    def parse_maze(self, raw_maze, width):
        return [raw_maze[i:i + width] for i in range(0, len(raw_maze), width)]

    def create_tile_details(self, wb, sb_dict, ab_dict, gob_dict, slb_dict, i, j, sector_maze, arena_maze,
                            game_object_maze, spawning_location_maze):
        tile_details = {
            "world": wb,
            "sector": sb_dict.get(sector_maze[i][j], ""),
            "arena": ab_dict.get(arena_maze[i][j], ""),
            "game_object": gob_dict.get(game_object_maze[i][j], ""),
            "spawning_location": slb_dict.get(spawning_location_maze[i][j], ""),
            "collision": collision_maze[i][j] != "0",
            "events": set()
        }
        return tile_details

    def add_tile_events(self):
        for i in range(self.maze_height):
            for j in range(self.maze_width):
                if self.tiles[i][j]["game_object"]:
                    object_name = ":".join([
                        self.tiles[i][j]["world"],
                        self.tiles[i][j]["sector"],
                        self.tiles[i][j]["arena"],
                        self.tiles[i][j]["game_object"]
                    ])
                    go_event = (object_name, None, None, None)
                    self.tiles[i][j]["events"].add(go_event)

    def map_address_to_tiles(self):
        address_tiles = {}
        for i in range(self.maze_height):
            for j in range(self.maze_width):
                addresses = []
                tile = self.tiles[i][j]
                if tile["sector"]:
                    addresses.append(f'{tile["world"]}:{tile["sector"]}')
                if tile["arena"]:
                    addresses.append(f'{tile["world"]}:{tile["sector"]}:{tile["arena"]}')
                if tile["game_object"]:
                    addresses.append(f'{tile["world"]}:{tile["sector"]}:{tile["arena"]}:{tile["game_object"]}')
                if tile["spawning_location"]:
                    addresses.append(f'<spawn_loc>{tile["spawning_location"]}')

                for add in addresses:
                    if add in address_tiles:
                        address_tiles[add].add((j, i))
                    else:
                        address_tiles[add] = {(j, i)}
        return address_tiles

    def turn_coordinate_to_tile(self, px_coordinate):
        x = math.ceil(px_coordinate[0] / self.sq_tile_size)
        y = math.ceil(px_coordinate[1] / self.sq_tile_size)
        return x, y

    def access_tile(self, tile):
        x, y = tile
        return self.tiles[y][x]

    def get_tile_path(self, tile, level):
        x, y = tile
        tile = self.tiles[y][x]
        path = tile['world']
        if level == "world":
            return path
        else:
            path += f":{tile['sector']}"
        if level == "sector":
            return path
        else:
            path += f":{tile['arena']}"
        if level == "arena":
            return path
        else:
            path += f":{tile['game_object']}"
        return path

    def get_nearby_tiles(self, tile, vision_r):
        x, y = tile
        left_end = max(0, x - vision_r)
        right_end = min(self.maze_width - 1, x + vision_r + 1)
        top_end = max(0, y - vision_r)
        bottom_end = min(self.maze_height - 1, y + vision_r + 1)

        nearby_tiles = []
        for i in range(left_end, right_end):
            for j in range(top_end, bottom_end):
                nearby_tiles.append((i, j))
        return nearby_tiles

    def add_event_from_tile(self, curr_event, tile):
        self.tiles[tile[1]][tile[0]]["events"].add(curr_event)

    def remove_event_from_tile(self, curr_event, tile):
        self.tiles[tile[1]][tile[0]]["events"].discard(curr_event)

    def turn_event_from_tile_idle(self, curr_event, tile):
        curr_tile_ev_cp = self.tiles[tile[1]][tile[0]]["events"].copy()
        for event in curr_tile_ev_cp:
            if event == curr_event:
                self.tiles[tile[1]][tile[0]]["events"].remove(event)
                new_event = (event[0], None, None, None)
                self.tiles[tile[1]][tile[0]]["events"].add(new_event)

    def remove_subject_events_from_tile(self, subject, tile):
        self.tiles[tile[1]][tile[0]]["events"] = {
            event for event in self.tiles[tile[1]][tile[0]]["events"] if event[0] != subject
        }