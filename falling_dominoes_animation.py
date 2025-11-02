"""
Blender Python Animation: Falling Dominoes
Complete script for creating a physics-based domino chain reaction animation
"""

import bpy
import math
import random
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
    bpy.context.scene.frame_end = 180
    bpy.context.scene.frame_set(1)
    
    # Add basic lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    area = bpy.context.active_object
    area.data.energy = 2.0
    area.data.size = 5.0
    
    # Add a third light for better illumination
    bpy.ops.object.light_add(type='AREA', location=(0, 5, 8))
    area2 = bpy.context.active_object
    area2.data.energy = 1.5
    area2.data.size = 3.0

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
        noise_tex.inputs['Scale'].default_value = 10.0
        mat.node_tree.links.new(noise_tex.outputs['Color'], bsdf.inputs['Base Color'])
        return mat
    
    # Connect nodes
    links = mat.node_tree.links
    links.new(tex_coord.outputs['UV'], image_tex.inputs['Vector'])
    links.new(image_tex.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_gradient_material(name, color1, color2):
    """Create a material with gradient effect"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # Clear default nodes
    mat.node_tree.nodes.clear()
    
    # Create nodes
    output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    tex_coord = mat.node_tree.nodes.new(type='ShaderNodeTexCoord')
    gradient_tex = mat.node_tree.nodes.new(type='ShaderNodeTexGradient')
    mix_rgb = mat.node_tree.nodes.new(type='ShaderNodeMixRGB')
    
    # Configure gradient
    gradient_tex.gradient_type = 'LINEAR'
    
    # Configure mix
    mix_rgb.blend_type = 'MIX'
    mix_rgb.inputs['Color1'].default_value = color1
    mix_rgb.inputs['Color2'].default_value = color2
    
    # Connect nodes
    links = mat.node_tree.links
    links.new(tex_coord.outputs['Generated'], gradient_tex.inputs['Vector'])
    links.new(gradient_tex.outputs['Color'], mix_rgb.inputs['Fac'])
    links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def setup_domino_scene():
    """Create dominoes and ground"""
    # Create FLAT ground (no tilt to prevent dominoes falling by themselves)
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground.rotation_euler = (0, 0, 0)  # Ensure ground is perfectly flat
    
    # Create and apply ground material
    try:
        ground_mat = create_textured_material("GroundMaterial", "//wood_texture.jpg")
    except:
        ground_mat = create_gradient_material("GroundMaterial", 
                                            (0.15, 0.1, 0.05, 1.0), 
                                            (0.25, 0.15, 0.1, 1.0))
        ground_mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.8
    apply_material(ground, ground_mat)
    
    # Create dominoes in a STRAIGHT line (no curve to prevent instability)
    dominoes = []
    domino_width = 0.3
    domino_height = 2.0
    domino_depth = 0.8
    spacing = 0.65  # Closer spacing for reliable chain reaction
    num_dominoes = 15  # Reduced for better performance
    
    for i in range(num_dominoes):
        x_pos = -5 + i * spacing
        y_pos = 0  # Straight line, no curve
        
        # No curve calculation needed - straight line
        angle = 0
        
        bpy.ops.mesh.primitive_cube_add(
            size=1,  # Create unit cube first
            location=(x_pos, y_pos, domino_height/2)
        )
        domino = bpy.context.active_object
        domino.name = f"Domino_{i:02d}"
        
        # Scale to domino proportions AFTER creation
        domino.scale = (domino_width, domino_depth, domino_height)
        
        # No rotation needed for straight line
        domino.rotation_euler = (0, 0, 0)
        
        # Create colorful material for each domino
        hue = i / num_dominoes  # Create rainbow effect
        color = (
            0.5 + 0.5 * math.cos(hue * 2 * math.pi),
            0.5 + 0.5 * math.cos(hue * 2 * math.pi + 2*math.pi/3),
            0.5 + 0.5 * math.cos(hue * 2 * math.pi + 4*math.pi/3),
            1.0
        )
        
        domino_mat = create_material(f"DominoMaterial_{i:02d}", color, roughness=0.3, metallic=0.1)
        apply_material(domino, domino_mat)
        
        dominoes.append(domino)
    
    return dominoes, ground

def setup_physics(dominoes, ground):
    """Set up rigid body physics for all objects"""
    # Add rigid body physics to all dominoes
    for i, domino in enumerate(dominoes):
        bpy.context.view_layer.objects.active = domino
        bpy.ops.rigidbody.object_add()
        domino.rigid_body.type = 'ACTIVE'
        domino.rigid_body.mass = 0.5
        domino.rigid_body.friction = 0.4
        domino.rigid_body.restitution = 0.1  # Low bounciness for realistic dominoes
        domino.rigid_body.linear_damping = 0.1
        domino.rigid_body.angular_damping = 0.1
        
        # Vary mass slightly for more interesting dynamics
        domino.rigid_body.mass = 0.4 + random.random() * 0.2
    
    # Add rigid body physics to ground
    bpy.context.view_layer.objects.active = ground
    bpy.ops.rigidbody.object_add()
    ground.rigid_body.type = 'PASSIVE'
    ground.rigid_body.friction = 0.8

def setup_camera():
    """Set up animated camera for dynamic viewing"""
    bpy.ops.object.camera_add(location=(0, -12, 6))
    camera = bpy.context.active_object
    camera.name = "AnimationCamera"
    bpy.context.scene.camera = camera
    
    # Animate camera to follow the domino action (4 keyframes for smooth tracking)
    # Start position - view from side angle to see ball and dominoes
    bpy.context.scene.frame_set(1)
    camera.location = (-6, -10, 5)
    camera.rotation_euler = (math.radians(65), 0, math.radians(10))
    camera.keyframe_insert(data_path="location", frame=1)
    camera.keyframe_insert(data_path="rotation_euler", frame=1)
    
    # Early-middle position - follow the falling action
    bpy.context.scene.frame_set(60)
    camera.location = (-2, -12, 6)
    camera.rotation_euler = (math.radians(60), 0, math.radians(5))
    camera.keyframe_insert(data_path="location", frame=60)
    camera.keyframe_insert(data_path="rotation_euler", frame=60)
    
    # Late-middle position - continue following
    bpy.context.scene.frame_set(120)
    camera.location = (2, -12, 6)
    camera.rotation_euler = (math.radians(60), 0, math.radians(-5))
    camera.keyframe_insert(data_path="location", frame=120)
    camera.keyframe_insert(data_path="rotation_euler", frame=120)
    
    # End position - show final dominoes falling
    bpy.context.scene.frame_set(180)
    camera.location = (6, -10, 5)
    camera.rotation_euler = (math.radians(65), 0, math.radians(-10))
    camera.keyframe_insert(data_path="location", frame=180)
    camera.keyframe_insert(data_path="rotation_euler", frame=180)
    
    return camera

def create_trigger_ball():
    """Create a ball to trigger the first domino"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(-10, 0, 3))
    ball = bpy.context.active_object
    ball.name = "TriggerBall"
    
    # Create ball material
    ball_mat = create_material("TriggerBallMaterial", (0.8, 0.2, 0.2, 1.0), 
                              roughness=0.1, metallic=0.3)
    apply_material(ball, ball_mat)
    
    # Add physics to ball with higher mass for more impact
    bpy.ops.rigidbody.object_add()
    ball.rigid_body.type = 'ACTIVE'
    ball.rigid_body.mass = 2.0  # Increased mass for better impact
    ball.rigid_body.friction = 0.4
    ball.rigid_body.restitution = 0.5
    ball.rigid_body.kinematic = True  # Start as kinematic (animation controlled)
    
    return ball

def animate_falling_dominoes():
    """Main animation function"""
    print("Setting up falling dominoes animation...")
    
    # Clear and setup scene
    clear_scene()
    setup_scene()
    
    # Create objects
    dominoes, ground = setup_domino_scene()
    
    # Create trigger ball
    trigger_ball = create_trigger_ball()
    
    # Set up physics
    setup_physics(dominoes, ground)
    
    # Set up camera
    setup_camera()
    
    # Set animation range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 180
    
    # Animate trigger ball with kinematic/physics hybrid approach
    # Get first domino position for accurate targeting
    first_domino = dominoes[0]
    domino_x = first_domino.location.x
    domino_y = first_domino.location.y
    
    # Use kinematic animation to push ball HORIZONTALLY on flat ground
    trigger_ball.rigid_body.kinematic = True
    
    bpy.context.scene.frame_set(1)
    trigger_ball.location = (domino_x - 3.0, domino_y, 1.0)  # Same height as domino base
    trigger_ball.keyframe_insert(data_path="location", frame=1)
    trigger_ball.rigid_body.keyframe_insert("kinematic", frame=1)
    
    # Ball rolls HORIZONTALLY toward the domino (no vertical drop)
    bpy.context.scene.frame_set(25)
    trigger_ball.location = (domino_x - 0.6, domino_y, 1.0)  # Horizontal movement only
    trigger_ball.keyframe_insert(data_path="location", frame=25)
    trigger_ball.rigid_body.keyframe_insert("kinematic", frame=25)
    
    # Switch to physics simulation after frame 25
    bpy.context.scene.frame_set(26)
    trigger_ball.rigid_body.kinematic = False
    trigger_ball.rigid_body.keyframe_insert("kinematic", frame=26)
    
    # Set up rigid body world
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    rigidbody_world = bpy.context.scene.rigidbody_world
    
    # Safely add objects to rigid body world (check if already added)
    if trigger_ball.name not in rigidbody_world.collection.objects:
        rigidbody_world.collection.objects.link(trigger_ball)
    for domino in dominoes:
        if domino.name not in rigidbody_world.collection.objects:
            rigidbody_world.collection.objects.link(domino)
    if ground.name not in rigidbody_world.collection.objects:
        rigidbody_world.collection.objects.link(ground)
    
    # Configure physics simulation
    rigidbody_world.point_cache.frame_start = 1
    rigidbody_world.point_cache.frame_end = 180
    
    # Set physics substeps for better accuracy (Blender 4.3+ attributes)
    rigidbody_world.substeps_per_frame = 10
    rigidbody_world.solver_iterations = 20
    
    # Add some visual effects
    add_particle_effects()
    
    # Bake physics simulation
    print("Baking physics simulation...")
    bpy.context.scene.frame_set(1)
    bpy.ops.ptcache.bake_all(bake=True)
    
    print("Falling dominoes animation setup complete!")
    print("Animation frames: 1-180")
    print("Press Spacebar to play the animation in Blender")

def add_particle_effects():
    """Add particle effects for more visual interest"""
    # Add particle system to ground for dust effect
    bpy.ops.mesh.primitive_plane_add(size=15, location=(0, 0, 0.01))
    dust_plane = bpy.context.active_object
    dust_plane.name = "DustPlane"
    
    # Hide dust plane from render but keep particles
    dust_plane.hide_render = True
    
    # Add particle system
    bpy.ops.object.particle_system_add()
    particle_system = dust_plane.particle_systems[0]
    settings = particle_system.settings
    
    # Configure particle settings (Blender 4.3+ uses 'EMITTER' instead of 'EMIT')
    settings.type = 'EMITTER'
    settings.emit_from = 'FACE'
    settings.count = 500
    settings.frame_start = 20
    settings.frame_end = 150
    settings.lifetime = 50
    settings.normal_factor = 0.1
    settings.factor_random = 0.5
    settings.angular_velocity_factor = 0.5
    settings.use_rotations = True
    settings.rotation_factor_random = 1.0
    
    # Set particle physics
    settings.physics_type = 'NEWTON'
    settings.factor_random = 0.5
    
    # Make particles small dust particles
    settings.particle_size = 0.02
    settings.size_random = 0.5
    
    # Create dust material
    dust_mat = create_material("DustMaterial", (0.6, 0.5, 0.4, 0.5))
    dust_mat.blend_method = 'BLEND'
    apply_material(dust_plane, dust_mat)

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
    
    # Enable motion blur for better animation quality
    bpy.context.scene.render.use_motion_blur = True
    bpy.context.scene.cycles.motion_blur_samples = 8
    
    # Set output path (use absolute path to avoid issues)
    import os
    output_dir = r"F:\blender2025\pertemuan3"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    bpy.context.scene.render.filepath = os.path.join(output_dir, "falling_dominoes_animation.mp4")

def render_animation():
    """Render the animation to file"""
    setup_render_settings()
    print("Rendering animation... This may take a while.")
    bpy.ops.render.render(animation=True)
    print(f"Animation rendered to: {bpy.context.scene.render.filepath}")

# Main execution
if __name__ == "__main__":
    # Create the animation
    animate_falling_dominoes()
    
    # Optional: Uncomment to render the animation
    # render_animation()
    
    print("\nAnimation complete!")
    print("To view the animation:")
    print("1. Press Spacebar in Blender to play")
    print("2. Or run render_animation() to export video")
    print("\nAnimation features:")
    print("- 15 colorful dominoes in a straight line arrangement")
    print("- Trigger ball to start the chain reaction")
    print("- Animated camera following the action")
    print("- Particle effects for dust")
    print("- Realistic physics simulation")