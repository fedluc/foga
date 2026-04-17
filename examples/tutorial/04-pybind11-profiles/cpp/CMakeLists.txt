cmake_minimum_required(VERSION 3.18)
project(hello_cpp_profiled LANGUAGES CXX)

include(CTest)

add_library(hello_core STATIC src/greeting.cpp)
target_compile_features(hello_core PUBLIC cxx_std_17)
target_include_directories(hello_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

add_executable(hello_cli app/main.cpp)
target_link_libraries(hello_cli PRIVATE hello_core)

add_executable(hello_cpp_tests tests/test_greeting.cpp)
target_link_libraries(hello_cpp_tests PRIVATE hello_core)

if(BUILD_TESTING)
  add_test(NAME hello_cpp_tests COMMAND hello_cpp_tests)
endif()
