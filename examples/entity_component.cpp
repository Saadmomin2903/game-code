#include <vector>
#include <string>
#include <memory>
#include <iostream>

// A simple game entity component system
class Component {
public:
    virtual ~Component() {}
    virtual void update(float deltaTime) = 0;
};

class Entity {
private:
    int id;
    std::string name;
    std::vector<std::shared_ptr<Component>> components;
    bool active;

public:
    Entity(int id, const std::string& name) : id(id), name(name), active(true) {}

    void addComponent(std::shared_ptr<Component> component) {
        components.push_back(component);
    }

    void update(float deltaTime) {
        if (!active) return;
        
        for (int i = 0; i < components.size(); i++) {
            components[i]->update(deltaTime);
        }
    }

    void setActive(bool isActive) {
        active = isActive;
    }

    bool isActive() const {
        return active;
    }

    int getId() const {
        return id;
    }

    std::string getName() const {
        return name;
    }
};

class TransformComponent : public Component {
private:
    float x, y, z;
    float rotationX, rotationY, rotationZ;
    float scaleX, scaleY, scaleZ;

public:
    TransformComponent() : x(0), y(0), z(0), rotationX(0), rotationY(0), rotationZ(0), scaleX(1), scaleY(1), scaleZ(1) {}

    void update(float deltaTime) override {
        // Transform logic would go here
    }

    void setPosition(float x, float y, float z) {
        this->x = x;
        this->y = y;
        this->z = z;
    }

    void setRotation(float x, float y, float z) {
        rotationX = x;
        rotationY = y;
        rotationZ = z;
    }

    void setScale(float x, float y, float z) {
        scaleX = x;
        scaleY = y;
        scaleZ = z;
    }
};

class RenderComponent : public Component {
private:
    std::string meshPath;
    std::string texturePath;
    bool visible;

public:
    RenderComponent(const std::string& mesh, const std::string& texture) 
        : meshPath(mesh), texturePath(texture), visible(true) {}

    void update(float deltaTime) override {
        // Rendering logic would go here
        if (visible) {
            // Render the mesh with texture
        }
    }

    void setVisible(bool isVisible) {
        visible = isVisible;
    }
};

class GameWorld {
private:
    std::vector<std::shared_ptr<Entity>> entities;
    float timeStep;

public:
    GameWorld() : timeStep(0.016f) {}

    std::shared_ptr<Entity> createEntity(const std::string& name) {
        int id = entities.size();
        auto entity = std::make_shared<Entity>(id, name);
        entities.push_back(entity);
        return entity;
    }

    void update() {
        for (auto& entity : entities) {
            if (entity->isActive()) {
                entity->update(timeStep);
            }
        }
    }

    void removeEntity(int id) {
        for (auto it = entities.begin(); it != entities.end(); ++it) {
            if ((*it)->getId() == id) {
                entities.erase(it);
                break;
            }
        }
    }
};

int main() {
    GameWorld world;
    
    // Create a player entity
    auto player = world.createEntity("Player");
    player->addComponent(std::make_shared<TransformComponent>());
    player->addComponent(std::make_shared<RenderComponent>("player.mesh", "player.png"));
    
    // Create an enemy entity
    auto enemy = world.createEntity("Enemy");
    enemy->addComponent(std::make_shared<TransformComponent>());
    enemy->addComponent(std::make_shared<RenderComponent>("enemy.mesh", "enemy.png"));
    
    // Game loop
    for (int i = 0; i < 100; i++) {
        world.update();
    }
    
    return 0;
}
