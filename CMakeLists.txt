cmake_minimum_required(VERSION 3.20)
project(bl4s_daq_sim CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_definitions(-DZMQ_BUILD_DRAFT_API=1)

find_package(PkgConfig REQUIRED)
set(ENV{PKG_CONFIG_PATH} "$ENV{HOME}/.local/lib64/pkgconfig:$ENV{HOME}/.local/share/pkgconfig:$ENV{PKG_CONFIG_PATH}")

pkg_check_modules(CNST REQUIRED ConstellationSatellite ConstellationExec)
find_package(ROOT REQUIRED COMPONENTS Core RIO Hist)

include_directories("$ENV{HOME}/.local/include" ${CNST_INCLUDE_DIRS})
link_directories("$ENV{HOME}/.local/lib64" ${CNST_LIBRARY_DIRS})

add_compile_options(${CNST_CFLAGS_OTHER})
# Yolu string literali olarak tanımlıyoruz (-DBUILD_LIBDIR="...")
add_definitions(-DBUILD_LIBDIR="${CMAKE_BINARY_DIR}")

macro(add_sat NAME SRC)
    add_library(${NAME} SHARED ${SRC})
    target_link_libraries(${NAME} PRIVATE ${CNST_LIBRARIES})
endmacro()

macro(add_sat_exec NAME SRC)
    add_executable(${NAME} ${SRC})
    target_link_libraries(${NAME} PRIVATE ${CNST_LIBRARIES})
endmacro()

add_sat(Detector src/DetectorSatellite.cpp)
add_sat_exec(detector_satellite src/main_detector.cpp)

add_sat(PollingTrigger src/PollingTriggerSatellite.cpp)
add_sat_exec(polling_trigger_satellite src/main_polling_trigger.cpp)

add_sat(StopController src/StopControllerSatellite.cpp)
add_sat_exec(stop_controller_satellite src/main_stop_controller.cpp)

add_library(CalorimeterMonitor SHARED src/CalorimeterMonitorSatellite.cpp src/MonitorCalorimeter.cpp)
target_include_directories(CalorimeterMonitor PRIVATE include ${ROOT_INCLUDE_DIRS})
target_link_libraries(CalorimeterMonitor PRIVATE ${CNST_LIBRARIES} ROOT::Core ROOT::RIO ROOT::Hist)

add_executable(calorimeter_monitor_satellite src/main_calorimeter_monitor.cpp)
target_link_libraries(calorimeter_monitor_satellite PRIVATE ${CNST_LIBRARIES})
