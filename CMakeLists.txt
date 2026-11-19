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

add_executable(easy1_bakery examples/easy1_bakery.cpp)
target_link_libraries(easy1_bakery PRIVATE minicplex_lib)

add_executable(easy2_projects examples/easy2_projects.cpp)
target_link_libraries(easy2_projects PRIVATE minicplex_lib)

enable_testing()
add_executable(minicplex_tests tests/test_solver.cpp)
target_link_libraries(minicplex_tests PRIVATE minicplex_lib)
add_test(NAME minicplex_tests COMMAND minicplex_tests)

add_executable(hard_production_plan examples/hard_production_plan.cpp)
target_link_libraries(hard_production_plan PRIVATE minicplex_lib)

add_executable(hard_staff_schedule examples/hard_staff_schedule.cpp)
target_link_libraries(hard_staff_schedule PRIVATE minicplex_lib)
