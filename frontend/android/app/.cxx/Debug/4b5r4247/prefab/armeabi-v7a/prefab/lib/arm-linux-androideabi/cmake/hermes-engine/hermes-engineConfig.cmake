if(NOT TARGET hermes-engine::hermesvm)
add_library(hermes-engine::hermesvm SHARED IMPORTED)
set_target_properties(hermes-engine::hermesvm PROPERTIES
    IMPORTED_LOCATION "/Users/lib-user/.gradle/caches/9.0.0/transforms/49151956c4ff43b077391c1ef3566f51/transformed/hermes-android-0.82.1-debug/prefab/modules/hermesvm/libs/android.armeabi-v7a/libhermesvm.so"
    INTERFACE_INCLUDE_DIRECTORIES "/Users/lib-user/.gradle/caches/9.0.0/transforms/49151956c4ff43b077391c1ef3566f51/transformed/hermes-android-0.82.1-debug/prefab/modules/hermesvm/include"
    INTERFACE_LINK_LIBRARIES ""
)
endif()

