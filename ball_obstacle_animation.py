"""
Blender Python Animation: Ball and Obstacle Collision
Complete script for creating a physics-based animation of a ball hitting an obstacle
"""

import bpy
import math
from mathutils import Vector

def clear_scene():
    """Clear all objects from the current scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def setup_scene():
    """Set up basic scene properties"""
    # Set frame rate and animation range
    bpy.context.scene.render.fps = 24
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120
    bpy.context.scene.frame_set(1)
    
    # Add basic lighting - BRIGHTER!
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5.0  # Increased from 3.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    area = bpy.context.active_object
    area.data.energy = 3.0  # Increased from 2.0
    area.data.size = 5.0
    
    # Add more lights untuk ball
    bpy.ops.object.light_add(type='POINT', location=(-8, 0, 5))
    point = bpy.context.active_object
    point.data.energy = 500.0  # Strong point light di ball
    
    bpy.ops.object.light_add(type='AREA', location=(0, -5, 5))
    area2 = bpy.context.active_object
    area2.data.energy = 2.0
    area2.data.size = 3.0
    
    # Set world background untuk ambient light
    world = bpy.context.scene.world
    if world:
        world.use_nodes = True
        bg = world.node_tree.nodes.get('Background')
        if bg:
            bg.inputs['Color'].default_value = (0.5, 0.5, 0.5, 1.0)  # Gray ambient
            bg.inputs['Strength'].default_value = 0.3  # Subtle ambient light

def create_material(name, color, roughness=0.5, metallic=0.0):
    """Create a basic material with specified properties"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # Get the Principled BSDF shader
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    
    return mat

def create_striped_material(name, color1, color2, scale=10.0):
    """Create a material with procedural stripes (untuk ball yang menarik)"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Roughness'].default_value = 0.2
    bsdf.inputs['Metallic'].default_value = 0.3
    
    # Wave texture for stripes
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-400, 0)
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = scale
    wave.inputs['Distortion'].default_value = 0.0
    
    # Texture coordinate
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    # Color ramp untuk definisi stripes
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 0)
    color_ramp.color_ramp.elements[0].color = color1
    color_ramp.color_ramp.elements[1].color = color2
    
    # Connect
    links.new(tex_coord.outputs['Generated'], wave.inputs['Vector'])
    links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def apply_material(obj, material):
    """Apply material to object"""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

def create_textured_material(name, image_path):
    """Create a material with texture"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # Clear default nodes
    mat.node_tree.nodes.clear()
    
    # Create nodes
    output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    tex_coord = mat.node_tree.nodes.new(type='ShaderNodeTexCoord')
    image_tex = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
    
    # Load image
    try:
        image = bpy.data.images.load(image_path)
        image_tex.image = image
    except:
        print(f"Could not load image: {image_path}")
        # Create a procedural texture as fallback
        noise_tex = mat.node_tree.nodes.new(type='ShaderNodeTexNoise')
        noise_tex.inputs['Scale'].default_value = 5.0
        mat.node_tree.links.new(noise_tex.outputs['Color'], bsdf.inputs['Base Color'])
        # FIX: Connect BSDF to Output!
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        return mat
    
    # Connect nodes
    links = mat.node_tree.links
    links.new(tex_coord.outputs['UV'], image_tex.inputs['Vector'])
    links.new(image_tex.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def setup_ball_obstacle_scene():
    """Create the ball, obstacle, and ground objects"""
    # Create ground plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    # Create and apply ground material with nice color
    ground_mat = create_material("GroundMaterial", (0.3, 0.35, 0.4, 1.0), roughness=0.8, metallic=0.0)
    apply_material(ground, ground_mat)
    
    # Create ball
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(-8, 0, 1))
    ball = bpy.context.active_object
    ball.name = "Ball"
    
    # Create and apply ball material - STRIPED PATTERN (seperti bola basket/soccer)
    ball_mat = create_striped_material(
        "BallMaterial", 
        color1=(0.95, 0.1, 0.1, 1.0),  # Bright red
        color2=(1.0, 1.0, 1.0, 1.0),   # White
        scale=15.0
    )
    apply_material(ball, ball_mat)
    print(f"✅ Ball material applied: {ball_mat.name}")
    print(f"   Ball has {len(ball.data.materials)} material(s)")
    if len(ball.data.materials) > 0:
        print(f"   Material name: {ball.data.materials[0].name}")
        print(f"   Uses nodes: {ball.data.materials[0].use_nodes}")
    
    # Create obstacle (wall) - positioned so bottom sits on ground
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obstacle = bpy.context.active_object
    obstacle.name = "Obstacle"
    obstacle.scale = (2, 2, 4)  # Scale to make it a tall wall (height=4)
    obstacle.location.z = 2  # Move up so bottom sits on ground (half of scaled height = 4/2 = 2)
    
    # Create and apply obstacle material - BRIGHT BLUE
    obstacle_mat = create_material("ObstacleMaterial", (0.1, 0.3, 0.9, 1.0), roughness=0.4, metallic=0.1)
    apply_material(obstacle, obstacle_mat)
    
    return ball, obstacle, ground

def setup_physics(ball, obstacle, ground):
    """Set up rigid body physics for all objects"""
    # Add rigid body physics to ball
    bpy.context.view_layer.objects.active = ball
    bpy.ops.rigidbody.object_add()
    ball.rigid_body.type = 'ACTIVE'
    ball.rigid_body.mass = 2.0
    ball.rigid_body.friction = 0.5
    ball.rigid_body.restitution = 0.8  # Bounciness
    ball.rigid_body.linear_damping = 0.1
    ball.rigid_body.angular_damping = 0.1
    ball.rigid_body.kinematic = True  # Start as kinematic for animation control
    ball.rigid_body.collision_shape = 'SPHERE'  # Sphere collision for ball
    ball.rigid_body.use_margin = True
    ball.rigid_body.collision_margin = 0.01
    
    # Add rigid body physics to obstacle (wall) - PASSIVE so it stays in place
    bpy.context.view_layer.objects.active = obstacle
    bpy.ops.rigidbody.object_add()
    obstacle.rigid_body.type = 'PASSIVE'  # Static wall - doesn't move
    obstacle.rigid_body.friction = 0.5
    obstacle.rigid_body.restitution = 0.3
    obstacle.rigid_body.collision_shape = 'BOX'  # Box collision for solid wall
    obstacle.rigid_body.use_margin = True
    obstacle.rigid_body.collision_margin = 0.01
    
    # Add rigid body physics to ground
    bpy.context.view_layer.objects.active = ground
    bpy.ops.rigidbody.object_add()
    ground.rigid_body.type = 'PASSIVE'
    ground.rigid_body.friction = 0.8
    ground.rigid_body.collision_shape = 'MESH'  # Mesh collision for ground
    ground.rigid_body.use_margin = True
    ground.rigid_body.collision_margin = 0.01

def setup_camera():
    """Set up camera for good viewing angle"""
    bpy.ops.object.camera_add(location=(8, -8, 6))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    bpy.context.scene.camera = camera
    
    # Add camera animation for better view
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    camera.keyframe_insert(data_path="rotation_euler", frame=1)
    
    bpy.context.scene.frame_set(60)
    camera.rotation_euler = (math.radians(50), 0, math.radians(35))
    camera.keyframe_insert(data_path="rotation_euler", frame=60)
    
    bpy.context.scene.frame_set(120)
    camera.rotation_euler = (math.radians(45), 0, math.radians(25))
    camera.keyframe_insert(data_path="rotation_euler", frame=120)

def animate_ball_collision():
    """Main animation function"""
    print("Setting up ball and obstacle animation...")
    
    # Clear and setup scene
    clear_scene()
    setup_scene()
    
    # Create objects
    ball, obstacle, ground = setup_ball_obstacle_scene()
    
    # Set up physics
    setup_physics(ball, obstacle, ground)
    
    # Set up camera
    setup_camera()
    
    # Set animation range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120
    
    # Animate ball using kinematic mode first, then switch to physics
    ball.rigid_body.kinematic = True
    
    # Frame 1: Ball starts position
    bpy.context.scene.frame_set(1)
    ball.location = (-8, 0, 3)
    ball.rotation_euler = (0, 0, 0)
    ball.keyframe_insert(data_path="location", frame=1)
    ball.keyframe_insert(data_path="rotation_euler", frame=1)
    ball.rigid_body.keyframe_insert("kinematic", frame=1)
    
    # Frame 20: Ball rolling toward obstacle (still kinematic)
    bpy.context.scene.frame_set(20)
    ball.location = (-2, 0, 1.5)
    ball.rotation_euler = (math.radians(180), 0, 0)
    ball.keyframe_insert(data_path="location", frame=20)
    ball.keyframe_insert(data_path="rotation_euler", frame=20)
    ball.rigid_body.keyframe_insert("kinematic", frame=20)
    
    # Frame 21: Switch to physics simulation
    bpy.context.scene.frame_set(21)
    ball.rigid_body.kinematic = False
    ball.rigid_body.keyframe_insert("kinematic", frame=21)
    
    # Set up rigid body world
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    rigidbody_world = bpy.context.scene.rigidbody_world
    rigidbody_world.collection.objects.link(ball)
    rigidbody_world.collection.objects.link(obstacle)
    rigidbody_world.collection.objects.link(ground)
    
    # Configure physics simulation
    rigidbody_world.point_cache.frame_start = 1
    rigidbody_world.point_cache.frame_end = 120
    
    # Set physics substeps for better accuracy
    rigidbody_world.steps_per_second = 120
    rigidbody_world.solver_iterations = 20
    
    # Bake physics simulation
    print("Baking physics simulation...")
    bpy.context.scene.frame_set(1)
    bpy.ops.ptcache.bake_all(bake=True)
    
    print("Ball and obstacle animation setup complete!")
    print("Animation frames: 1-120")
    print("Press Spacebar to play the animation in Blender")

def setup_render_settings():
    """Configure render settings for output"""
    # Set render engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    
    # Set output format
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    
    # Set resolution
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 100
    
    # Set samples for quality
    bpy.context.scene.cycles.samples = 128
    
    # Set output path
    bpy.context.scene.render.filepath = "//ball_obstacle_animation.mp4"

def render_animation():
    """Render the animation to file"""
    setup_render_settings()
    print("Rendering animation... This may take a while.")
    bpy.ops.render.render(animation=True)
    print(f"Animation rendered to: {bpy.context.scene.render.filepath}")

# Main execution
if __name__ == "__main__":
    # Create the animation
    animate_ball_collision()
    
    # Optional: Uncomment to render the animation
    # render_animation()
    
    print("\nAnimation complete!")
    print("To view the animation:")
    print("1. Press Spacebar in Blender to play")
    print("2. Or run render_animation() to export video")