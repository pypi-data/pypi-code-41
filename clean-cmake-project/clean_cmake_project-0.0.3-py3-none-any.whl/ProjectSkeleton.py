#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime
import stringcase

src = "src"
tests = "tests"
libs = "libs"
cmake = "CMakeLists.txt"
host = os.getlogin()
now = datetime.today().strftime('%Y-%m-%d')


class ProjectBuilder:
    def __init__(self, project_name, path_input, exe_suffix):

        if os.path.exists(path_input):
            print("Path exists !!")
        else:
            path_input = os.getcwd()
            print("Path does not exist ! -> default to current directory", path_input)

        self.path = path_input
        self.base_const = stringcase.constcase(os.path.basename(self.path))
        self.base_snake = stringcase.snakecase(os.path.basename(self.path))
        print("Current working directory %s" % self.path)

        self.snake = stringcase.snakecase(project_name)
        self.const = stringcase.constcase(project_name)
        self.pascal = stringcase.pascalcase(project_name)

        self.create_base()
        self.create_project()
        if exe_suffix is not None:
            exe_project_name = "_".join([stringcase.snakecase(project_name), exe_suffix])
            self.exe_snake = stringcase.snakecase(exe_project_name)
            self.exe_const = stringcase.constcase(exe_project_name)
            self.exe_pascal = stringcase.pascalcase(exe_project_name)
            self.create_executable()

        # print current projects
        print("Current source projects: ")
        for d in next(os.walk(os.path.join(self.path, src)))[1]:
            print("\t", d)

        # print current projects
        print("Current source projects - tests: ")
        for d in next(os.walk(os.path.join(self.path, tests)))[1]:
            print("\t", d)

    def create_base(self):

        def download_gtest():
            if not os.path.exists(os.path.join(self.path, libs)):
                os.mkdir(os.path.join(self.path, libs))
                if not os.path.exists(os.path.join(self.path, libs, "googletest")):
                    os.chdir(os.path.join(self.path, libs))
                    gtest_path = "https://github.com/google/googletest.git"
                    os.system("git clone " + gtest_path)
                    os.chdir("..")

        def create_cmake():
            if not os.path.exists(os.path.join(self.path, cmake)):
                cmake_string = ("cmake_minimum_required(VERSION 3.10)\n"
                                "project({})\n"
                                "\n"
                                "set(CMAKE_CXX_STANDARD 17)\n"
                                "\n"
                                "include_directories(src)\n"
                                "\n"
                                "add_subdirectory(libs/googletest)\n"
                                ).format(self.base_snake)
                with open(os.path.join(self.path, cmake), "w+") as cmake_file:
                    cmake_file.write(cmake_string)

        create_cmake()
        download_gtest()
        if not os.path.exists(os.path.join(self.path, tests)):
            os.mkdir(os.path.join(self.path, tests))
        if not os.path.exists(os.path.join(self.path, src)):
            os.mkdir(os.path.join(self.path, src))

    def create_project(self):

        def append_to_cmake():
            # add_subdirectory to CMakeFile
            cmake_string = ("\n"
                            "add_subdirectory({1}/{0})\n"
                            "add_subdirectory({2}/{0}_test)\n"
                            ).format(self.snake, src, tests)
            with open(os.path.join(self.path, cmake), "a") as cmake_file:
                cmake_file.write(cmake_string)

        def create_src():
            src_path = os.path.join(self.path, src, self.snake)
            os.mkdir(src_path)
            cmake_string = ("cmake_minimum_required(VERSION 3.10)\n"
                            "project({0})\n"
                            "\n"
                            "set(CMAKE_CXX_STANDARD 17)\n"
                            "\n"
                            "set({1}_SOURCE_FILES\n"
                            "        {2}.cpp {2}.h\n"
                            "    )\n"
                            "\n"
                            "add_library({0} ${{{1}_SOURCE_FILES}})\n").format(self.snake, self.const, self.pascal)
            with open(os.path.join(src_path, cmake), 'w+') as f:
                f.write(cmake_string)

            h_string = ("//\n"
                        "// Created by {0} on {1}.\n"
                        "//\n"
                        "\n"
                        "#ifndef {4}_{2}_H\n"
                        "#define {4}_{2}_H  \n"
                        "\n"
                        "class {3} {{\n"
                        "\n"
                        "}}; \n"
                        "\n"
                        "#endif //{4}_{2}_H\n"
                        ).format(host, now, self.const, self.pascal, self.base_const)
            with open(os.path.join(src_path, self.pascal + ".h"), 'w+') as f:
                f.write(h_string)

            cpp_string = ("//\n"
                          "// Created by {0} on {1}.\n"
                          "//\n"
                          "#include \"{2}.h\"\n"
                          ).format(host, now, self.pascal)
            with open(os.path.join(src_path, self.pascal + ".cpp"), 'w+') as f:
                f.write(cpp_string)

        def create_test():
            tests_path = os.path.join(self.path, tests, self.snake + "_test")
            os.mkdir(tests_path)

            cmake_string = ("cmake_minimum_required(VERSION 3.10)\n"
                            "project({0})\n"
                            "\n"
                            "enable_testing()\n"
                            "include_directories(${{gtest_SOURCE_DIR}}/include ${{gtest_SOURCE_DIR}})\n"
                            "set({1}_TEST_FILES\n"
                            "        {2}_tests.cpp\n"
                            "    )\n"
                            "add_executable(run{3}Tests ${{{1}_TEST_FILES}})\n"
                            "target_link_libraries(run{3}Tests gtest gtest_main)\n"
                            "target_link_libraries(run{3}Tests {2})\n"
                            ).format(tests, self.const, self.snake, self.pascal)
            with open(os.path.join(tests_path, cmake), 'w+') as f:
                f.write(cmake_string)

            cpp_string = ("//\n"
                          "// Created by {0} on {1}.\n"
                          "//\n"
                          "#include \"{3}/{2}.h\"\n"
                          "#include \"gtest/gtest.h\"\n"
                          "\n"
                          "\n"
                          "TEST(basic_{3}_check, test_eq){{\n"
                          "\tEXPECT_EQ(1, 1);\n"
                          "}}\n"
                          "\n"
                          "TEST(basic_{3}_check, test_neq){{\n"
                          "\tEXPECT_NE(1, 0);\n"
                          "}}\n"
                          "\n"
                          ).format(host, now, self.pascal, self.snake)
            with open(os.path.join(tests_path, self.snake + "_tests.cpp"), 'w+') as f:
                f.write(cpp_string)

        if os.path.exists(os.path.join(self.path, src, self.snake)):
            print("Folder already exists", self.snake)
        else:
            append_to_cmake()
            create_src()
            create_test()

    def create_executable(self):

        def append_to_cmake():
            # add_subdirectory to CMakeFile
            cmake_string = ("\n"
                            "add_subdirectory({1}/{0})\n"
                            ).format(self.exe_snake, src)
            with open(os.path.join(self.path, cmake), "a") as cmake_file:
                cmake_file.write(cmake_string)

        def create_src():
            src_path = os.path.join(self.path, src, self.exe_snake)
            os.mkdir(src_path)
            cmake_string = ("cmake_minimum_required(VERSION 3.10)\n"
                            "project({0})\n"
                            "\n"
                            "set(CMAKE_CXX_STANDARD 17)\n"
                            "\n"
                            "set({1}_FILES\n"
                            "        {2}.cpp\n"
                            "    )\n"
                            "\n"
                            "add_executable({0} ${{{1}_FILES}})\n"
                            "\n"
                            "set_target_properties({0} PROPERTIES ENABLE_EXPORTS 1)\n"
                            "\n"
                            "target_link_libraries({0}\n"
                            "       {3}\n"
                            "       )\n"
                            ).format(self.exe_snake, self.exe_const, self.exe_pascal, self.snake)
            with open(os.path.join(src_path, cmake), 'w+') as f:
                f.write(cmake_string)

            cpp_string = ("//\n"
                          "// Created by {0} on {1}.\n"
                          "//\n"
                          "#include <iostream>\n"
                          "#include <{2}/{3}.h>\n"
                          "\n"
                          "void run(){{\n"
                          "    std::cout << \"Project Backbone is set!\" << std::endl;\n"
                          "}}\n"
                          "\n"
                          "int main(){{\n"
                          "    run();\n"
                          "    return 0;\n"
                          "}}\n"
                          "\n"
                          ).format(host, now, self.snake, self.pascal)
            with open(os.path.join(src_path, self.exe_pascal + ".cpp"), 'w+') as f:
                f.write(cpp_string)

        if os.path.exists(os.path.join(self.path, src, self.exe_snake)):
            print("Executable Folder already exists", self.exe_snake)
        else:
            append_to_cmake()
            create_src()


def main():
    name = input("Enter New Project Name: ")
    print("Project name from input", name)
    path = input("Enter Folder Path: ")
    print("Path from input", path)
    exe_suffix = input("Enter Executable suffix (Leave blank if no executable): ")
    if exe_suffix is not None:
        print("Executable suffix", exe_suffix)
    ProjectBuilder(name, path, exe_suffix)


if __name__ == "__main__":
    main()
