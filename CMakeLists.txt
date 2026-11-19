cmake_minimum_required(VERSION 3.14)
project(minicplex VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

add_library(minicplex_lib
  src/model.cpp
  src/simplex.cpp
  src/branch_and_bound.cpp
  src/lp_reader.cpp)
target_include_directories(minicplex_lib PUBLIC include)
target_compile_options(minicplex_lib PRIVATE -Wall -Wextra)

add_executable(minicplex src/main.cpp)
target_link_libraries(minicplex PRIVATE minicplex_lib)

add_executable(api_demo examples/api_demo.cpp)
target_link_libraries(api_demo PRIVATE minicplex_lib)

enable_testing()
add_executable(minicplex_tests tests/test_solver.cpp)
target_link_libraries(minicplex_tests PRIVATE minicplex_lib)
add_test(NAME minicplex_tests COMMAND minicplex_tests)
