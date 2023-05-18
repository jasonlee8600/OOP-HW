// GET HELP IN OFFICE HOURS
#include "SmartPointer.hpp"
#include "LinkedList.hpp"

int main() {
    // write example here
    SmartPointer<Node<int>> sp1(new Node<int>(10));
    SmartPointer<Node<int>> sp2(new Node<int>(11));
    sp1->setNext(sp2);
    sp2->setNext(sp1);
    return 0;
}


// EXPLANATION

// When two or more objects refer to each other in a cycle, each object will have a reference count greater than zero,
    // preventing them from being deallocated by the reference counting SmartPointer. 

    // In the code above, we create two nodes sp1 and sp2 with an initial ref_count of 1
        // I then make each node's next member reference the other node, which makes each node's reference counter go up by 1 to 2
        // When the SmartPointers sp1 and sp2 go out of scope, their destructors are called, 
        // but the reference counts of the nodes will not reach zero because each node has a reference to the other. 
        // Therefore, the objects will not be deallocated, resulting in a memory leak.
    
    // To avoid this problem, languages like Python and Java use a more sophisticated form of garbage collection, 
        // known as cyclic garbage collection, which can detect and remove cycles of objects that refer to each other.