#include <vector>
#include <cmath>
#include <iostream>

// A simple physics system for a game
class PhysicsSystem {
private:
    struct Vector2 {
        float x;
        float y;
        
        Vector2() : x(0.0f), y(0.0f) {}
        Vector2(float x, float y) : x(x), y(y) {}
        
        float magnitude() {
            return sqrt(x * x + y * y);
        }
        
        void normalize() {
            float mag = magnitude();
            if (mag > 0) {
                x = x / mag;
                y = y / mag;
            }
        }
    };
    
    struct PhysicsObject {
        Vector2 position;
        Vector2 velocity;
        Vector2 acceleration;
        float mass;
        bool isStatic;
        
        PhysicsObject() : mass(1.0f), isStatic(false) {}
    };
    
    std::vector<PhysicsObject> objects;
    Vector2 gravity;
    float timeStep;
    
public:
    PhysicsSystem() : gravity(0.0f, -9.8f), timeStep(0.016f) {}
    
    void addObject(float x, float y, float mass, bool isStatic) {
        PhysicsObject obj;
        obj.position = Vector2(x, y);
        obj.mass = mass;
        obj.isStatic = isStatic;
        objects.push_back(obj);
    }
    
    void update() {
        for (int i = 0; i < objects.size(); i++) {
            if (objects[i].isStatic)
                continue;
            
            // Apply gravity
            objects[i].acceleration.x = gravity.x;
            objects[i].acceleration.y = gravity.y;
            
            // Update velocity
            objects[i].velocity.x += objects[i].acceleration.x * timeStep;
            objects[i].velocity.y += objects[i].acceleration.y * timeStep;
            
            // Update position
            objects[i].position.x += objects[i].velocity.x * timeStep;
            objects[i].position.y += objects[i].velocity.y * timeStep;
            
            // Simple ground collision
            if (objects[i].position.y < 0) {
                objects[i].position.y = 0;
                objects[i].velocity.y = -objects[i].velocity.y * 0.5f; // Bounce with energy loss
            }
        }
    }
    
    void printObjectPositions() {
        for (int i = 0; i < objects.size(); i++) {
            std::cout << "Object " << i << " position: (" 
                      << objects[i].position.x << ", " 
                      << objects[i].position.y << ")" << std::endl;
        }
    }
};

int main() {
    PhysicsSystem physics;
    
    // Add some objects
    physics.addObject(0.0f, 10.0f, 1.0f, false); // Falling object
    physics.addObject(5.0f, 0.0f, 10.0f, true);  // Static object
    
    // Simulate for a few steps
    for (int i = 0; i < 100; i++) {
        physics.update();
        if (i % 10 == 0) {
            std::cout << "Step " << i << ":" << std::endl;
            physics.printObjectPositions();
        }
    }
    
    return 0;
}
