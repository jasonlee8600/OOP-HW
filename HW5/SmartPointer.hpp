#pragma once

#include <cstddef>

class ReferenceCounter
{
    int count; // Reference count
public:
    void increment() {
        count++;
    }
    int decrement() {
        return --count;
    }
};

template <typename T>
class SmartPointer
{
    // private instance variables for dumb pointer and ReferenceCounter
    T* dumb_ptr;
    ReferenceCounter* ref_counter;

public:

    SmartPointer(T *pValue) : dumb_ptr(pValue), ref_counter(0){
        // initialize dumb pointer
        // set up and increment reference counter
        ref_counter = new ReferenceCounter();
        ref_counter->increment();
    }

    // Copy constructor
    SmartPointer(const SmartPointer<T> &sp) {
        // Copy the data and reference pointer
        dumb_ptr = sp.dumb_ptr;
        ref_counter = sp.ref_counter;
        // increment the reference count
        ref_counter->increment();
    }

    // Destructor
    ~SmartPointer() {
        // Decrement the reference count
        int count = ref_counter->decrement();
        // if reference become zero delete the data
        if(count == 0){
            delete dumb_ptr;
            delete ref_counter;
        }
    }

    T& operator*() {
        // delegate
        return *dumb_ptr;
    }

    T* operator->() {
        // delegate
        return dumb_ptr;
    }

    // Assignment operator
    SmartPointer<T> &operator=(const SmartPointer<T> &sp)
    {
        // Deal with old SmartPointer that is being overwritten
        if(this != &sp) {
            int count = ref_counter->decrement();

            if(count == 0){
                delete dumb_ptr;
                delete ref_counter;
            }

            // Copy sp into this (similar to copy constructor)
            dumb_ptr = sp.dumb_ptr;
            ref_counter = sp.ref_counter;
            ref_counter->increment();
        }
        // return this
        return *this;
    }

    // Check equal to nullptr
    bool operator==(std::nullptr_t rhs) const
    {
        return dumb_ptr == rhs;
    }
};