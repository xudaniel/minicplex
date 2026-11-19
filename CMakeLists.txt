cmake_minimum_required(VERSION 3.14)
project(minicplex VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# 内存 / 未定义行为检查：cmake -DMINICPLEX_SANITIZE=ON -DCMAKE_BUILD_TYPE=Debug
option(MINICPLEX_SANITIZE "Build with AddressSanitizer + UndefinedBehaviorSanitizer" OFF)
if(MINICPLEX_SANITIZE)
  add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all)
  add_link_options(-fsanitize=address,undefined)
endif()

add_library(minicplex_lib
  src/model.cpp
  src/simplex.cpp
  src/branch_and_bound.cpp
  src/presolve.cpp
  src/lp_reader.cpp)
target_include_directories(minicplex_lib PUBLIC include)
target_compile_options(minicplex_lib PRIVATE -Wall -Wextra)

add_executable(minicplex src/main.cpp)
target_link_libraries(minicplex PRIVATE minicplex_lib)

# 例子
foreach(ex api_demo easy1_bakery easy2_projects hard_production_plan hard_staff_schedule)
  add_executable(${ex} examples/${ex}.cpp)
  target_link_libraries(${ex} PRIVATE minicplex_lib)
endforeach()

# 入门例子（examples/basics）
set(BASICS 01_one_variable 02_two_variables 03_must_be_whole 04_yes_or_no 05_minimize)
foreach(ex ${BASICS})
  add_executable(basics_${ex} examples/basics/${ex}.cpp)
  target_link_libraries(basics_${ex} PRIVATE minicplex_lib)
endforeach()

# 工具：随机模型生成器、批量求解 / 基准
add_executable(minicplex_gen tools/gen_random.cpp)
target_link_libraries(minicplex_gen PRIVATE minicplex_lib)
add_executable(minicplex_bench tools/bench.cpp)
target_link_libraries(minicplex_bench PRIVATE minicplex_lib)

# 测试
enable_testing()
add_executable(minicplex_tests tests/test_solver.cpp)
target_link_libraries(minicplex_tests PRIVATE minicplex_lib)
add_test(NAME unit_tests COMMAND minicplex_tests)

# 冒烟测试：每个例子都要能跑通（退出码 0）
foreach(ex api_demo easy1_bakery easy2_projects hard_production_plan hard_staff_schedule)
  add_test(NAME example_${ex} COMMAND ${ex})
endforeach()
foreach(lp production knapsack facility mixed bakery)
  add_test(NAME cli_${lp} COMMAND minicplex --quiet ${CMAKE_SOURCE_DIR}/examples/${lp}.lp)
endforeach()
foreach(ex ${BASICS})
  add_test(NAME basics_${ex} COMMAND basics_${ex})
endforeach()
# --trace 跟踪输出（学习用）也要能正常运行
add_test(NAME cli_trace COMMAND minicplex --trace ${CMAKE_SOURCE_DIR}/examples/bakery.lp)
add_test(NAME cli_trace_plain COMMAND minicplex --trace --no-presolve --cuts 0 --branch frac ${CMAKE_SOURCE_DIR}/examples/bakery.lp)
# 基准模型全部能解且解可行
add_test(NAME bench_models COMMAND minicplex_bench --quiet ${CMAKE_SOURCE_DIR}/bench/models)
