from src import devices, devices_custom_lru_cache
import timeit

def test_functools_cache():
    start = timeit.default_timer()
    devices.get_device_configuration(1)
    end = timeit.default_timer()
    elapsed = end - start
    assert elapsed >= 0.1, "should NOT be cached"

    start = timeit.default_timer()
    devices.get_device_configuration(1)
    end = timeit.default_timer()
    elapsed = end - start
    assert elapsed < 0.1, "should be cached"

def test_functools_cache_maxitems():
    #warm up cache
    for i in range(100): #0,1,...99
        devices.get_device_configuration(i)
    
    devices.get_device_configuration(100) #should drop 0
    
    start = timeit.default_timer()
    devices.get_device_configuration(0)
    end = timeit.default_timer()
    elapsed = end - start
    assert elapsed >= 0.1, "should NOT be cached"


def test_custom_cache():
    cache = devices_custom_lru_cache.LRUCache(devices_custom_lru_cache.__get_device_configuration, 10)

    start = timeit.default_timer()
    devices_custom_lru_cache.get_device_configuration(1, cache)
    end = timeit.default_timer()
    elapsed = end - start
    assert elapsed >= 0.1, "should NOT be cached"

    start = timeit.default_timer()
    devices_custom_lru_cache.get_device_configuration(1, cache)
    end = timeit.default_timer()
    elapsed = end - start
    assert elapsed < 0.1, "should be cached"

def test_custom_cache_maxitems():
    cache = devices_custom_lru_cache.LRUCache(devices_custom_lru_cache.__get_device_configuration, 10)

    #warm up cache
    for i in range(10): #0,1,...99
        devices_custom_lru_cache.get_device_configuration(i, cache)
    
    devices_custom_lru_cache.get_device_configuration(100) #should drop 0
    
    start = timeit.default_timer()
    devices_custom_lru_cache.get_device_configuration(0)
    end = timeit.default_timer()
    elapsed = end - start
    assert elapsed >= 0.1, "should NOT be cached"