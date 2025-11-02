import bpy
import math
import random

def clear_scene():
    """Remove all objects from the scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear orphaned data
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

def create_material(name, color, roughness=0.5, metallic=0.0):
    """Create a material with specified color and properties"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.location = (0, 0)
    
    # Create output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Link nodes
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def apply_material(obj, material):
    """Apply material to object"""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

def create_tank(location=(0, -10, 0)):
    """Create a simple tank with body, turret, and barrel"""
    tank_parts = []
    
    # Tank body (base) - position so bottom sits on ground
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], 0))
    body = bpy.context.active_object
    body.name = "TankBody"
    body.scale = (3, 4, 1.5)  # Wide and long body
    body.location.z = 0.75  # Half of scaled height (1.5/2), so bottom at Z=0
    body_mat = create_material("TankBodyMat", (0.2, 0.3, 0.2, 1.0), roughness=0.7, metallic=0.3)
    apply_material(body, body_mat)
    tank_parts.append(body)
    
    # Tank turret (rotating part) - centered on body top
    turret_z = 0.75 + 0.75 + 0.5  # body center + body half height + turret half height = 2.0
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=1, location=(location[0], location[1], turret_z))
    turret = bpy.context.active_object
    turret.name = "TankTurret"
    turret.rotation_euler = (0, 0, 0)
    turret_mat = create_material("TankTurretMat", (0.3, 0.4, 0.3, 1.0), roughness=0.6, metallic=0.4)
    apply_material(turret, turret_mat)
    tank_parts.append(turret)
    
    # Tank barrel (gun) - attached to turret front
    barrel_z = turret_z  # Same height as turret center
    barrel_y = location[1] + 2  # Extended forward from turret
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=4, location=(location[0], barrel_y, barrel_z))
    barrel = bpy.context.active_object
    barrel.name = "TankBarrel"
    barrel.rotation_euler = (math.radians(90), 0, 0)  # Point forward
    barrel_mat = create_material("TankBarrelMat", (0.1, 0.1, 0.1, 1.0), roughness=0.3, metallic=0.8)
    apply_material(barrel, barrel_mat)
    tank_parts.append(barrel)
    
    # Parent turret and barrel to body properly with keep transform
    bpy.context.view_layer.objects.active = body
    turret.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    turret.select_set(False)
    
    bpy.context.view_layer.objects.active = turret
    barrel.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    barrel.select_set(False)
    
    # Add tracks/wheels for better look (optional decorative elements)
    # Left track
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0] - 1.8, location[1], 0))
    left_track = bpy.context.active_object
    left_track.name = "LeftTrack"
    left_track.scale = (0.5, 4.5, 0.8)
    left_track.location.z = 0.4
    left_track_mat = create_material("TrackMat", (0.15, 0.15, 0.15, 1.0), roughness=0.8, metallic=0.2)
    apply_material(left_track, left_track_mat)
    # Parent left track to body
    bpy.context.view_layer.objects.active = body
    left_track.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    left_track.select_set(False)
    tank_parts.append(left_track)
    
    # Right track
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0] + 1.8, location[1], 0))
    right_track = bpy.context.active_object
    right_track.name = "RightTrack"
    right_track.scale = (0.5, 4.5, 0.8)
    right_track.location.z = 0.4
    apply_material(right_track, left_track_mat)
    # Parent right track to body
    bpy.context.view_layer.objects.active = body
    right_track.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    right_track.select_set(False)
    tank_parts.append(right_track)
    
    return body, turret, barrel, tank_parts

def create_target_objects():
    """Create 5 target objects arranged in an arc"""
    targets = []
    colors = [
        (0.8, 0.2, 0.2, 1.0),  # Red
        (0.2, 0.8, 0.2, 1.0),  # Green
        (0.2, 0.2, 0.8, 1.0),  # Blue
        (0.8, 0.8, 0.2, 1.0),  # Yellow
        (0.8, 0.2, 0.8, 1.0),  # Magenta
    ]
    
    # Arrange targets in an arc
    for i in range(5):
        angle = math.radians(-60 + (i * 30))  # -60° to +60°
        distance = 15
        x = distance * math.sin(angle)
        y = distance * math.cos(angle)
        z = 1.5  # Height off ground
        
        # Create cube target
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0))
        target = bpy.context.active_object
        target.name = f"Target_{i+1}"
        target.scale = (2, 2, 3)  # Tall target
        target.location.z = 1.5  # Bottom sits on ground
        
        # Apply colored material
        target_mat = create_material(f"TargetMat_{i+1}", colors[i], roughness=0.4, metallic=0.1)
        apply_material(target, target_mat)
        
        targets.append(target)
    
    return targets

def create_missile(start_location):
    """Create a missile projectile"""
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.5, location=start_location)
    missile = bpy.context.active_object
    missile.name = "Missile"
    missile.rotation_euler = (math.radians(90), 0, 0)  # Point forward
    
    # Missile material (dark gray/black)
    missile_mat = create_material("MissileMat", (0.15, 0.15, 0.15, 1.0), roughness=0.3, metallic=0.7)
    apply_material(missile, missile_mat)
    
    return missile

def create_dust_particle_system(target, frame):
    """Create dust particle explosion at target location"""
    # Create emitter plane at target location
    location = target.location.copy()
    bpy.ops.mesh.primitive_plane_add(size=0.1, location=location)
    emitter = bpy.context.active_object
    emitter.name = f"DustEmitter_{target.name}"
    
    # Add particle system
    bpy.ops.object.particle_system_add()
    psys = emitter.particle_systems[0]
    pset = psys.settings
    
    # Particle settings
    pset.name = f"Dust_{target.name}"
    pset.count = 100  # Number of particles
    pset.frame_start = frame
    pset.frame_end = frame + 1
    pset.lifetime = 30  # How long particles last
    pset.emit_from = 'FACE'
    pset.normal_factor = 2.0  # Spread outward
    pset.factor_random = 1.5
    
    # Physics
    pset.physics_type = 'NEWTON'
    pset.mass = 0.1
    pset.particle_size = 0.15
    pset.size_random = 0.5
    
    # Gravity and damping
    pset.effector_weights.gravity = 0.5
    pset.damping = 0.5
    
    # Render settings
    pset.render_type = 'OBJECT'
    
    # Create small cube for particle instance
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(100, 100, 100))  # Off screen
    particle_obj = bpy.context.active_object
    particle_obj.name = f"DustParticle_{target.name}"
    
    # Color particle same as target
    if target.data.materials:
        particle_obj.data.materials.append(target.data.materials[0])
    
    pset.instance_object = particle_obj
    
    return emitter, particle_obj

def setup_ground():
    """Create ground plane"""
    bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    
    ground_mat = create_material("GroundMat", (0.4, 0.35, 0.3, 1.0), roughness=0.9, metallic=0.0)
    apply_material(ground, ground_mat)
    
    return ground

def setup_lighting():
    """Add lighting to the scene"""
    # Sun light
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), math.radians(30), 0)
    
    return sun

def setup_camera(tank_body):
    """Set up camera to view the scene"""
    # Camera position - behind and above tank
    cam_location = (0, -20, 8)
    bpy.ops.object.camera_add(location=cam_location)
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(65), 0, 0)
    bpy.context.scene.camera = camera
    
    return camera

def animate_tank_missile_destruction():
    """Main animation function"""
    # Clear scene
    clear_scene()
    
    # Setup scene parameters
    bpy.context.scene.render.fps = 24
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 300
    bpy.context.scene.frame_set(1)
    
    # Enable gravity
    bpy.context.scene.gravity = (0, 0, -9.81)
    
    # Create scene elements
    ground = setup_ground()
    sun = setup_lighting()
    
    # Create tank
    tank_body, tank_turret, tank_barrel, tank_parts = create_tank(location=(0, -10, 0))
    
    # Create targets
    targets = create_target_objects()
    
    # Setup camera
    camera = setup_camera(tank_body)
    
    # Animation timing
    # Each missile fires 50 frames apart
    missile_intervals = 50
    missiles = []
    emitters = []
    particle_objects = []
    
    for i, target in enumerate(targets):
        # Calculate timing for this missile
        fire_frame = 1 + (i * missile_intervals)
        impact_frame = fire_frame + 30  # Missile takes 30 frames to reach target
        
        # Rotate turret to face target at firing frame
        bpy.context.scene.frame_set(fire_frame - 10)  # Start rotating 10 frames before
        
        # Calculate angle to target (FIXED: negate angle to point correctly)
        target_x = target.location.x
        target_y = target.location.y
        tank_y = tank_body.location.y
        
        # Negate the angle so turret points TOWARD target, not away
        angle_to_target = -math.atan2(target_x, target_y - tank_y)
        
        # Animate turret rotation
        tank_turret.rotation_euler.z = 0
        tank_turret.keyframe_insert(data_path="rotation_euler", frame=fire_frame - 10)
        
        tank_turret.rotation_euler.z = angle_to_target
        tank_turret.keyframe_insert(data_path="rotation_euler", frame=fire_frame)
        
        # Create missile
        barrel_tip_y = tank_body.location.y + 4
        barrel_tip_z = tank_body.location.z + 1.5
        missile_start = (target_x * 0.1, barrel_tip_y, barrel_tip_z)  # Start near barrel
        
        missile = create_missile(missile_start)
        missiles.append(missile)
        
        # Animate missile from barrel to target
        bpy.context.scene.frame_set(fire_frame)
        missile.location = missile_start
        missile.keyframe_insert(data_path="location", frame=fire_frame)
        missile.scale = (1, 1, 1)
        missile.keyframe_insert(data_path="scale", frame=fire_frame)
        
        # Missile flies to target
        bpy.context.scene.frame_set(impact_frame)
        missile.location = target.location.copy()
        missile.keyframe_insert(data_path="location", frame=impact_frame)
        
        # Missile disappears at impact
        bpy.context.scene.frame_set(impact_frame + 1)
        missile.scale = (0.01, 0.01, 0.01)
        missile.keyframe_insert(data_path="scale", frame=impact_frame + 1)
        
        # Target disappears at impact (turns to dust)
        bpy.context.scene.frame_set(impact_frame)
        target.scale = (2, 2, 3)
        target.keyframe_insert(data_path="scale", frame=impact_frame)
        
        bpy.context.scene.frame_set(impact_frame + 1)
        target.scale = (0.01, 0.01, 0.01)
        target.keyframe_insert(data_path="scale", frame=impact_frame + 1)
        
        # Create dust particle system at impact
        emitter, particle_obj = create_dust_particle_system(target, impact_frame)
        emitters.append(emitter)
        particle_objects.append(particle_obj)
    
    # Reset to frame 1
    bpy.context.scene.frame_set(1)
    
    print("=" * 60)
    print("✓ TANK MISSILE ANIMATION CREATED!")
    print("=" * 60)
    print(f"✓ Tank created at Y=-10")
    print(f"✓ {len(targets)} targets arranged in arc")
    print(f"✓ {len(missiles)} missiles created")
    print(f"✓ Animation: Frames 1-{bpy.context.scene.frame_end}")
    print(f"✓ Each missile fires every {missile_intervals} frames")
    print(f"✓ Targets explode into dust particles on impact")
    print("=" * 60)
    print("\nTIMELINE:")
    for i in range(5):
        fire = 1 + (i * missile_intervals)
        impact = fire + 30
        print(f"  Target {i+1}: Fire frame {fire} → Impact frame {impact}")
    print("=" * 60)
    print("\nPress SPACEBAR in viewport to play animation!")
    print("Tip: Switch to 'Rendered' viewport shading for particles")

# Run the animation
if __name__ == "__main__":
    animate_tank_missile_destruction()
