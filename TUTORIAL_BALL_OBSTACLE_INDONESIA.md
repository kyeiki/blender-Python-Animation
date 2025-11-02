# Tutorial: Membuat Animasi Bola Menabrak Obstacle di Blender dengan Python

## Daftar Isi
1. [Pengenalan](#pengenalan)
2. [Persiapan](#persiapan)
3. [Konsep Physics Simulation](#konsep-physics-simulation)
4. [Langkah 1: Membersihkan Scene](#langkah-1-membersihkan-scene)
5. [Langkah 2: Setup Scene dan Lighting](#langkah-2-setup-scene-dan-lighting)
6. [Langkah 3: Membuat Material](#langkah-3-membuat-material)
7. [Langkah 4: Membuat Objek (Ball, Obstacle, Ground)](#langkah-4-membuat-objek)
8. [Langkah 5: Setup Rigid Body Physics](#langkah-5-setup-rigid-body-physics)
9. [Langkah 6: Collision Shapes](#langkah-6-collision-shapes)
10. [Langkah 7: Animasi Kinematic-Dynamic Hybrid](#langkah-7-animasi-kinematic-dynamic-hybrid)
11. [Langkah 8: Setup Camera](#langkah-8-setup-camera)
12. [Langkah 9: Baking Physics](#langkah-9-baking-physics)
13. [Langkah 10: Render Settings](#langkah-10-render-settings)
14. [Troubleshooting Physics](#troubleshooting-physics)
15. [Tuning Physics Parameters](#tuning-physics-parameters)

---

## Pengenalan

Tutorial ini mengajarkan cara membuat animasi fisika sederhana namun realistis: bola yang berguling dan menabrak dinding (obstacle).

🎯 **Fitur Animasi:**
- Bola merah berguling dari kiri ke kanan
- Dinding biru sebagai obstacle
- Collision realistis dengan bouncing
- Ground plane sebagai lantai
- Camera tracking yang smooth

**Konsep Yang Dipelajari:**
- **Rigid Body Physics**: Simulasi objek padat
- **Collision Detection**: Deteksi tabrakan akurat
- **Kinematic vs Dynamic**: Kontrol manual vs physics
- **Physics Properties**: Mass, friction, restitution
- **Collision Shapes**: SPHERE, BOX, MESH

---

## Persiapan

### Kebutuhan:
- **Blender 4.3** atau lebih baru
- Pemahaman dasar physics (gravitasi, momentum)
- File texture (opsional): concrete, ball, wall

### Timeline Animasi:

```
Frame 1-20:  Kinematic animation (kontrol manual)
             Bola berguling dari kiri mendekati dinding
             
Frame 21:    Switch ke dynamic physics
             Physics engine mengambil alih
             
Frame 21-120: Physics simulation
             Bola menabrak dinding, memantul, jatuh
```

**Total Durasi:** 120 frame = 5 detik pada 24 fps

---

## Konsep Physics Simulation

### Rigid Body Types:

1. **ACTIVE** (Dynamic)
   - Dipengaruhi gravitasi
   - Bereaksi terhadap collision
   - Bisa bergerak bebas
   - Contoh: Bola, box yang jatuh

2. **PASSIVE** (Static)
   - Tidak dipengaruhi gravitasi
   - Tidak bergerak sendiri
   - Bisa ditabrak objek ACTIVE
   - Contoh: Dinding, lantai

3. **KINEMATIC** (Animated)
   - Bergerak sesuai keyframe animation
   - Tidak dipengaruhi gravitasi
   - Bisa collision dengan objek lain
   - Contoh: Platform bergerak, door

### Physics Properties:

```
Mass (Massa):
- Berat objek dalam kilogram
- Lebih berat = lebih sulit bergerak
- Contoh: Bola = 2 kg, Mobil = 1000 kg

Friction (Gesekan):
- Resistensi saat bergesekan
- 0.0 = licin sempurna (es)
- 1.0 = sangat kasar (sandpaper)
- Contoh: Bola = 0.5 (sedang)

Restitution (Bounciness):
- Tingkat pantulan
- 0.0 = tidak memantul (tanah liat)
- 1.0 = memantul sempurna (bola karet)
- Contoh: Bola basket = 0.8

Damping (Redaman):
- Hambatan gerakan (seperti hambatan udara)
- Linear: Untuk gerakan translasi
- Angular: Untuk rotasi
- Contoh: 0.1 = sedikit hambatan
```

---

## Langkah 1: Membersihkan Scene

```python
def clear_scene():
    """Clear all objects from the current scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
```

**Penjelasan:**
- `select_all(action='SELECT')`: Pilih semua objek di scene
- `delete(use_global=False)`: Hapus hanya di scene aktif
- `use_global=False`: Tidak menghapus objek di scene lain

**Fungsi:** Memastikan scene bersih sebelum membuat animasi baru.

---

## Langkah 2: Setup Scene dan Lighting

```python
def setup_scene():
    """Set up basic scene properties"""
    # Set frame rate dan animation range
    bpy.context.scene.render.fps = 24
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120
    bpy.context.scene.frame_set(1)
```

**Parameter Scene:**
- `fps = 24`: Frame per second (standar film)
- `frame_start = 1`: Mulai dari frame 1
- `frame_end = 120`: Total 120 frame (5 detik)
- `frame_set(1)`: Reset timeline ke awal

### Lighting Setup

```python
    # Sun light (cahaya utama)
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
```

**Sun Light:**
- Type: Directional (parallel rays)
- Energy: 3.0 (cukup terang)
- Location: Tidak penting (infinite distance)

```python
    # Area light (fill light)
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    area = bpy.context.active_object
    area.data.energy = 2.0
    area.data.size = 5.0
```

**Area Light:**
- Type: Soft diffuse light
- Size: 5.0 (area besar = cahaya lebih soft)
- Energy: 2.0 (lebih redup dari sun)

**Setup 2 Lampu:**
- Sun: Main light (key light)
- Area: Fill light (mengurangi shadow gelap)

---

## Langkah 3: Membuat Material

### Material Dasar

```python
def create_material(name, color, roughness=0.5, metallic=0.0):
    """Create a basic material with specified properties"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    
    return mat
```

**Principled BSDF Inputs:**
- **Base Color**: RGBA (Red, Green, Blue, Alpha)
  - Nilai 0.0 - 1.0 untuk setiap channel
  - Contoh: (0.8, 0.2, 0.2, 1.0) = Merah cerah
  
- **Roughness**: Kekasaran permukaan
  - 0.0 = Mirror (cermin sempurna)
  - 0.5 = Satin (agak mengkilap)
  - 1.0 = Matte (tidak mengkilap sama sekali)
  
- **Metallic**: Tingkat metalik
  - 0.0 = Non-metal (plastik, kayu, kain)
  - 0.5 = Semi-metal
  - 1.0 = Metal murni (chrome, gold)

### Material dengan Tekstur

```python
def create_textured_material(name, image_path):
    """Create a material with texture"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    # Clear default nodes
    mat.node_tree.nodes.clear()
```

**Node System:**
Kita membuat node graph untuk tekstur:

```
[Texture Coordinate] → [Image Texture] → [Principled BSDF] → [Material Output]
```

```python
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
        # Fallback: Use procedural noise
        noise_tex = mat.node_tree.nodes.new(type='ShaderNodeTexNoise')
        mat.node_tree.links.new(noise_tex.outputs['Color'], bsdf.inputs['Base Color'])
        return mat
```

**Try-Except Block:**
- `try`: Coba load gambar dari file
- `except`: Jika gagal, gunakan noise texture sebagai fallback

**Image Path:**
- `"//concrete_texture.jpg"`: Relative path (dalam folder .blend)
- Prefix `//` = relative to .blend file location

### Apply Material ke Objek

```python
def apply_material(obj, material):
    """Apply material to object"""
    if obj.data.materials:
        obj.data.materials[0] = material  # Replace existing
    else:
        obj.data.materials.append(material)  # Add new
```

**Logic:**
1. Cek apakah objek sudah punya material
2. Jika ada: replace material pertama
3. Jika tidak: tambahkan material baru

---

## Langkah 4: Membuat Objek

### Ground Plane (Lantai)

```python
def setup_ball_obstacle_scene():
    """Create the ball, obstacle, and ground objects"""
    # Create ground plane
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
```

**Properti Ground:**
- Size: 20 unit (cukup besar untuk animasi)
- Location: (0, 0, 0) = titik origin
- Z = 0: Ground level (reference)

**Material Ground:**
```python
    try:
        ground_mat = create_textured_material("GroundMaterial", "//concrete_texture.jpg")
    except:
        ground_mat = create_material("GroundMaterial", (0.3, 0.3, 0.3, 1.0), roughness=0.8)
    apply_material(ground, ground_mat)
```

- Warna: Abu-abu (0.3, 0.3, 0.3)
- Roughness: 0.8 (cukup kasar)

### Ball (Bola)

```python
    # Create ball
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(-8, 0, 1))
    ball = bpy.context.active_object
    ball.name = "Ball"
```

**UV Sphere:**
- `radius=1`: Diameter 2 unit
- `location=(-8, 0, 1)`:
  - X = -8: Jauh di kiri
  - Y = 0: Center
  - Z = 1: Radius di atas ground (bottom touches ground)

**Perhitungan Z:**
```
Radius = 1
Bottom of sphere = Center Z - Radius
1 - 1 = 0 (touches ground) ✅
```

**Material Ball:**
```python
    try:
        ball_mat = create_textured_material("BallMaterial", "//ball_texture.jpg")
    except:
        ball_mat = create_material("BallMaterial", (0.8, 0.2, 0.2, 1.0), 
                                   roughness=0.2, metallic=0.1)
    apply_material(ball, ball_mat)
```

- Warna: Merah cerah (0.8, 0.2, 0.2)
- Roughness: 0.2 (mengkilap seperti bola basket)
- Metallic: 0.1 (sedikit efek metalik)

### Obstacle (Dinding)

```python
    # Create obstacle (wall)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obstacle = bpy.context.active_object
    obstacle.name = "Obstacle"
    obstacle.scale = (2, 2, 4)  # Lebar, Dalam, Tinggi
    obstacle.location.z = 2  # Half of scaled height
```

**Perhitungan Posisi Z:**
```
Scale Z = 4 (tinggi dinding)
Center harus di: 4 / 2 = 2
Sehingga:
- Bottom di: 2 - 2 = 0 (ground level) ✅
- Top di: 2 + 2 = 4 (ketinggian 4 unit)
```

**Kenapa Z = 2?**
Cube default center di origin. Setelah scale Z=4:
- Tanpa offset: bottom di -2, top di +2 ❌
- Dengan Z=2: bottom di 0, top di 4 ✅

**Material Obstacle:**
```python
    try:
        obstacle_mat = create_textured_material("ObstacleMaterial", "//wall_texture.jpg")
    except:
        obstacle_mat = create_material("ObstacleMaterial", (0.2, 0.4, 0.8, 1.0), 
                                       roughness=0.3, metallic=0.0)
    apply_material(obstacle, obstacle_mat)
```

- Warna: Biru (0.2, 0.4, 0.8)
- Roughness: 0.3 (cukup smooth)
- Metallic: 0.0 (non-metal)

---

## Langkah 5: Setup Rigid Body Physics

### Ball Physics (ACTIVE)

```python
def setup_physics(ball, obstacle, ground):
    """Set up rigid body physics for all objects"""
    # Add rigid body physics to ball
    bpy.context.view_layer.objects.active = ball
    bpy.ops.rigidbody.object_add()
    ball.rigid_body.type = 'ACTIVE'
```

**Steps:**
1. Set ball sebagai active object
2. Add rigid body component
3. Set type = 'ACTIVE' (dynamic)

**Physics Properties:**
```python
    ball.rigid_body.mass = 2.0
    ball.rigid_body.friction = 0.5
    ball.rigid_body.restitution = 0.8
    ball.rigid_body.linear_damping = 0.1
    ball.rigid_body.angular_damping = 0.1
```

**Penjelasan Parameter:**

| Property | Value | Artinya |
|----------|-------|---------|
| `mass` | 2.0 | Berat 2 kg (bola basket ~0.6 kg, bowling ball ~7 kg) |
| `friction` | 0.5 | Gesekan sedang (tidak licin, tidak lengket) |
| `restitution` | 0.8 | Bouncy (memantul 80% dari tinggi awal) |
| `linear_damping` | 0.1 | Sedikit hambatan gerakan lurus |
| `angular_damping` | 0.1 | Sedikit hambatan rotasi |

**Kinematic Mode:**
```python
    ball.rigid_body.kinematic = True  # Start as kinematic
```

**Kenapa Start Kinematic?**
- Kita ingin kontrol presisi di awal
- Bola berguling dengan path yang pasti
- Switch ke dynamic setelah mendekati dinding

### Obstacle Physics (PASSIVE)

```python
    # Add rigid body physics to obstacle (wall)
    bpy.context.view_layer.objects.active = obstacle
    bpy.ops.rigidbody.object_add()
    obstacle.rigid_body.type = 'PASSIVE'  # Static wall
    obstacle.rigid_body.friction = 0.5
    obstacle.rigid_body.restitution = 0.3
```

**PASSIVE Properties:**
- `type = 'PASSIVE'`: Dinding tidak bergerak
- `friction = 0.5`: Sama dengan bola
- `restitution = 0.3`: Dinding tidak bouncy (absorb energy)

**Kenapa PASSIVE?**
- Dinding harus tetap di tempat
- Tidak dipengaruhi gravitasi
- Tetap bisa collision dengan objek ACTIVE

### Ground Physics (PASSIVE)

```python
    # Add rigid body physics to ground
    bpy.context.view_layer.objects.active = ground
    bpy.ops.rigidbody.object_add()
    ground.rigid_body.type = 'PASSIVE'
    ground.rigid_body.friction = 0.8
```

**Ground Properties:**
- `type = 'PASSIVE'`: Lantai statis
- `friction = 0.8`: Friction tinggi (tidak licin)

---

## Langkah 6: Collision Shapes

### Ball - SPHERE Shape

```python
    ball.rigid_body.collision_shape = 'SPHERE'
    ball.rigid_body.use_margin = True
    ball.rigid_body.collision_margin = 0.01
```

**SPHERE Collision:**
- Paling akurat untuk bola
- Collision detection lebih efisien
- Rolling physics lebih realistis

**Collision Margin:**
- `use_margin = True`: Enable safety margin
- `collision_margin = 0.01`: 0.01 unit gap
- Mencegah objek "stuck" atau "tembus"

### Obstacle - BOX Shape

```python
    obstacle.rigid_body.collision_shape = 'BOX'
    obstacle.rigid_body.use_margin = True
    obstacle.rigid_body.collision_margin = 0.01
```

**BOX Collision:**
- Perfect untuk dinding/cube
- 6 flat faces untuk collision
- Lebih akurat daripada MESH untuk box

### Ground - MESH Shape

```python
    ground.rigid_body.collision_shape = 'MESH'
    ground.rigid_body.use_margin = True
    ground.rigid_body.collision_margin = 0.01
```

**MESH Collision:**
- Menggunakan geometry exact
- Perlu untuk plane (tidak punya volume)
- Lebih lambat tapi lebih akurat

**Collision Shapes Comparison:**

| Shape | Best For | Performance | Accuracy |
|-------|----------|-------------|----------|
| SPHERE | Balls, rounded objects | ⚡⚡⚡ Fast | ⭐⭐⭐ Perfect |
| BOX | Cubes, walls, containers | ⚡⚡ Good | ⭐⭐⭐ Perfect |
| CYLINDER | Cans, poles, wheels | ⚡⚡ Good | ⭐⭐ Good |
| CAPSULE | Characters, pills | ⚡⚡ Good | ⭐⭐ Good |
| CONE | Cone shapes | ⚡⚡ Good | ⭐⭐ Good |
| CONVEX_HULL | Complex but convex | ⚡ Slow | ⭐⭐ Good |
| MESH | Any shape (PASSIVE only) | 🐌 Very Slow | ⭐⭐⭐ Perfect |

---

## Langkah 7: Animasi Kinematic-Dynamic Hybrid

### Strategi Hybrid

```
Frame 1-20:  KINEMATIC mode
             Manual animation dengan keyframes
             Bola berguling terkontrol
             
Frame 21+:   DYNAMIC mode
             Physics engine mengambil alih
             Collision, bouncing, gravity aktif
```

### Keyframe 1: Start Position

```python
def animate_ball_collision():
    # ... setup ...
    
    # Frame 1: Ball starts position
    bpy.context.scene.frame_set(1)
    ball.location = (-8, 0, 3)
    ball.rotation_euler = (0, 0, 0)
    ball.keyframe_insert(data_path="location", frame=1)
    ball.keyframe_insert(data_path="rotation_euler", frame=1)
    ball.rigid_body.keyframe_insert("kinematic", frame=1)
```

**Posisi Awal:**
- X = -8: Jauh di kiri
- Y = 0: Center
- Z = 3: Di atas (untuk jatuh sedikit)
- Rotation = (0, 0, 0): No rotation yet

### Keyframe 20: Approaching Obstacle

```python
    # Frame 20: Ball rolling toward obstacle
    bpy.context.scene.frame_set(20)
    ball.location = (-2, 0, 1.5)
    ball.rotation_euler = (math.radians(180), 0, 0)
    ball.keyframe_insert(data_path="location", frame=20)
    ball.keyframe_insert(data_path="rotation_euler", frame=20)
    ball.rigid_body.keyframe_insert("kinematic", frame=20)
```

**Posisi Frame 20:**
- X = -2: Dekat dengan dinding (dinding di X=0)
- Z = 1.5: Turun sedikit (dari 3 ke 1.5)
- Rotation X = 180°: Bola berputar (rolling effect)

**Perhitungan Rotasi:**
```
Distance traveled: -8 to -2 = 6 units
Ball circumference: 2πr = 2π(1) = 6.28 units
Rotations: 6 / 6.28 ≈ 0.95 rotations
Angle: 0.95 × 360° ≈ 342° ≈ 180° (setengah putaran lebih)
```

### Switch ke Dynamic Physics

```python
    # Frame 21: Switch to physics simulation
    bpy.context.scene.frame_set(21)
    ball.rigid_body.kinematic = False
    ball.rigid_body.keyframe_insert("kinematic", frame=21)
```

**Momen Kritis:**
- Frame 20: `kinematic = True` (manual control)
- Frame 21: `kinematic = False` (physics aktif)
- Dari frame 21 onwards, gravity dan collision aktif

**Kenapa Frame 21?**
- Bola sudah dekat dengan dinding
- Punya momentum horizontal dari keyframe animation
- Collision akan terjadi secara natural

---

## Langkah 8: Setup Camera

```python
def setup_camera():
    """Set up camera for good viewing angle"""
    bpy.ops.object.camera_add(location=(8, -8, 6))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    bpy.context.scene.camera = camera
```

**Camera Position:**
- X = 8: Kanan (melihat dari samping kanan)
- Y = -8: Belakang (overview shot)
- Z = 6: Tinggi (bird's eye view angle)
- Rotation: 60° pitch, 45° yaw

**Visualisasi:**
```
        Camera (8, -8, 6)
              ↘
               ↘ 60° down, 45° angle
                ↘
        Scene Center (0, 0, 0)
```

### Camera Animation

```python
    # Keyframe 1
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    camera.keyframe_insert(data_path="rotation_euler", frame=1)
    
    # Keyframe 60
    bpy.context.scene.frame_set(60)
    camera.rotation_euler = (math.radians(50), 0, math.radians(35))
    camera.keyframe_insert(data_path="rotation_euler", frame=60)
    
    # Keyframe 120
    bpy.context.scene.frame_set(120)
    camera.rotation_euler = (math.radians(45), 0, math.radians(25))
    camera.keyframe_insert(data_path="rotation_euler", frame=120)
```

**Camera Movement:**
```
Frame 1:   Pitch 60°, Yaw 45° (steep angle)
Frame 60:  Pitch 50°, Yaw 35° (following ball)
Frame 120: Pitch 45°, Yaw 25° (wider view)
```

**Efek:**
Camera bergerak smooth mengikuti aksi bola.

---

## Langkah 9: Baking Physics

### Setup Rigid Body World

```python
    # Set up rigid body world
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    rigidbody_world = bpy.context.scene.rigidbody_world
```

**Rigid Body World:**
System yang mengelola semua physics objects.

### Add Objects to World

```python
    rigidbody_world.collection.objects.link(ball)
    rigidbody_world.collection.objects.link(obstacle)
    rigidbody_world.collection.objects.link(ground)
```

**Collection:**
Semua objek physics harus ada dalam rigid body collection.

### Configure Simulation

```python
    # Configure physics simulation
    rigidbody_world.point_cache.frame_start = 1
    rigidbody_world.point_cache.frame_end = 120
    
    # Set physics substeps for better accuracy
    rigidbody_world.steps_per_second = 120
    rigidbody_world.solver_iterations = 20
```

**Parameters:**

**Steps Per Second:**
- `120`: Physics dihitung 120x per detik
- FPS = 24, substeps = 120/24 = 5 per frame
- Lebih tinggi = lebih akurat, lebih lambat

**Solver Iterations:**
- `20`: Solver mencoba 20x per step
- Resolve collision conflicts
- Lebih tinggi = lebih stabil

### Bake Simulation

```python
    # Bake physics simulation
    print("Baking physics simulation...")
    bpy.context.scene.frame_set(1)
    bpy.ops.ptcache.bake_all(bake=True)
```

**Baking Process:**
1. Hitung physics untuk setiap frame
2. Simpan hasilnya di cache
3. Playback real-time tanpa re-calculate

**Kenapa Bake?**
- Physics calculation lambat
- Baking = pre-calculate semua
- Playback jauh lebih smooth

---

## Langkah 10: Render Settings

```python
def setup_render_settings():
    """Configure render settings for output"""
    # Set render engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
```

**Render Engine:**
- **CYCLES**: Path tracing (realistis)
- **EEVEE**: Real-time (cepat)
- `device = 'GPU'`: Gunakan GPU (lebih cepat)

### Output Format

```python
    # Set output format
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
```

**Video Encoding:**
- `FFMPEG`: Video encoding library
- `MPEG4`: MP4 container
- `H264`: Compression codec (standard)
- `constant_rate_factor = 'MEDIUM'`: Balance quality/size

### Resolution

```python
    # Set resolution
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 100
```

- 1920×1080: Full HD
- `percentage = 100`: Full resolution

### Samples

```python
    # Set samples for quality
    bpy.context.scene.cycles.samples = 128
```

**Samples:**
- 128 = good quality dengan noise minimal
- Lebih tinggi = lebih smooth, lebih lambat
- Untuk test: 32-64 samples cukup

### Output Path

```python
    # Set output path
    bpy.context.scene.render.filepath = "//ball_obstacle_animation.mp4"
```

- `//`: Relative path (sama folder dengan .blend)
- Output: `ball_obstacle_animation.mp4`

---

## Troubleshooting Physics

### Problem 1: Bola Tembus Dinding

**Gejala:** Bola melewati dinding tanpa collision

**Penyebab:**
1. Collision shape tidak di-set
2. Substeps terlalu rendah
3. Bola terlalu cepat

**Solusi:**
```python
# 1. Set collision shapes
ball.rigid_body.collision_shape = 'SPHERE'  # ✅
obstacle.rigid_body.collision_shape = 'BOX'  # ✅

# 2. Increase substeps
rigidbody_world.steps_per_second = 240  # Dari 120 jadi 240

# 3. Reduce ball speed
# Ubah keyframe agar bola bergerak lebih pelan
```

### Problem 2: Bola Tidak Jatuh

**Gejala:** Bola melayang di udara

**Penyebab:**
1. Masih kinematic mode
2. Gravity tidak aktif

**Solusi:**
```python
# 1. Pastikan switch ke dynamic
ball.rigid_body.kinematic = False  # Frame 21+

# 2. Cek gravity
bpy.context.scene.gravity = (0, 0, -9.81)  # Default Earth gravity
```

### Problem 3: Bola Tidak Memantul

**Gejala:** Bola hanya jatuh, tidak bounce

**Penyebab:**
1. Restitution terlalu rendah
2. Damping terlalu tinggi

**Solusi:**
```python
# 1. Increase restitution
ball.rigid_body.restitution = 0.8  # Bouncy

# 2. Reduce damping
ball.rigid_body.linear_damping = 0.05  # Lebih rendah
```

### Problem 4: Bola Berputar Aneh

**Gejala:** Rotasi tidak natural

**Penyebab:**
1. Angular damping salah
2. Friction tidak sesuai

**Solusi:**
```python
# 1. Adjust angular damping
ball.rigid_body.angular_damping = 0.1  # Sedang

# 2. Match friction
ball.rigid_body.friction = 0.5
ground.rigid_body.friction = 0.8  # Ground lebih tinggi
```

### Problem 5: Collision Tidak Akurat

**Gejala:** Bola "stuck" atau jitter

**Penyebab:**
1. Collision margin terlalu besar/kecil
2. Solver iterations rendah

**Solusi:**
```python
# 1. Tune collision margin
ball.rigid_body.collision_margin = 0.01  # Small but not zero

# 2. Increase solver iterations
rigidbody_world.solver_iterations = 30  # Dari 20 jadi 30
```

---

## Tuning Physics Parameters

### Restitution (Bounciness) Guide

```python
# Basketball
ball.rigid_body.restitution = 0.8  # Very bouncy

# Tennis ball
ball.rigid_body.restitution = 0.7  # Bouncy

# Soccer ball
ball.rigid_body.restitution = 0.6  # Medium bounce

# Bowling ball
ball.rigid_body.restitution = 0.2  # Low bounce

# Clay ball
ball.rigid_body.restitution = 0.0  # No bounce
```

### Friction Guide

```python
# Ice (very slippery)
obj.rigid_body.friction = 0.1

# Wood on wood
obj.rigid_body.friction = 0.4

# Rubber on concrete
obj.rigid_body.friction = 0.7

# Sandpaper
obj.rigid_body.friction = 1.0
```

### Mass Guide

```python
# Ping pong ball
ball.rigid_body.mass = 0.003  # 3 grams

# Tennis ball
ball.rigid_body.mass = 0.058  # 58 grams

# Basketball
ball.rigid_body.mass = 0.624  # 624 grams

# Bowling ball
ball.rigid_body.mass = 7.0  # 7 kg

# Car
car.rigid_body.mass = 1500  # 1.5 tons
```

### Damping Guide

```python
# No air resistance (vacuum)
obj.rigid_body.linear_damping = 0.0
obj.rigid_body.angular_damping = 0.0

# Normal air (default)
obj.rigid_body.linear_damping = 0.04
obj.rigid_body.angular_damping = 0.1

# Underwater
obj.rigid_body.linear_damping = 0.8
obj.rigid_body.angular_damping = 0.8

# Thick oil
obj.rigid_body.linear_damping = 0.95
obj.rigid_body.angular_damping = 0.95
```

---

## Advanced Techniques

### 1. Multiple Balls

```python
# Create 5 balls
balls = []
for i in range(5):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=1, 
        location=(-8, i * 2 - 4, 3)  # Spread in Y-axis
    )
    ball = bpy.context.active_object
    ball.name = f"Ball_{i}"
    
    # Setup physics
    bpy.ops.rigidbody.object_add()
    ball.rigid_body.type = 'ACTIVE'
    # ... physics properties ...
    
    balls.append(ball)
```

### 2. Force Field (Wind/Gravity)

```python
# Add wind force
bpy.ops.object.effector_add(type='WIND', location=(0, 0, 5))
wind = bpy.context.active_object
wind.field.strength = 5.0
wind.field.flow = 0.5  # Turbulence
```

### 3. Fracture on Impact

```python
# Addon: Cell Fracture
# Break obstacle into pieces on impact

# Detect collision frame
impact_frame = 25

# At impact, replace obstacle with fractured version
# Enable physics for each piece
```

### 4. Trail Effect

```python
# Add motion blur
bpy.context.scene.render.use_motion_blur = True
bpy.context.scene.cycles.motion_blur_samples = 8

# Or add particle trail
bpy.ops.object.particle_system_add()
psys = ball.particle_systems[0]
psys.settings.count = 100
psys.settings.lifetime = 10  # Short trail
```

### 5. Slow Motion

```python
# Change time scale
bpy.context.scene.rigidbody_world.time_scale = 0.5  # Half speed

# Or adjust frame rate
bpy.context.scene.render.fps = 48  # Twice normal speed
# Keep animation at 24fps, render at 48fps = slow motion
```

---

## Optimization Tips

### 1. Reduce Substeps untuk Preview

```python
# Preview mode (fast)
rigidbody_world.steps_per_second = 60  # Dari 120

# Final render (accurate)
rigidbody_world.steps_per_second = 240
```

### 2. Use Simple Collision Shapes

```python
# ❌ Slow:
obj.rigid_body.collision_shape = 'MESH'

# ✅ Fast:
obj.rigid_body.collision_shape = 'BOX'  # or SPHERE
```

### 3. Reduce Solver Iterations untuk Test

```python
# Test mode
rigidbody_world.solver_iterations = 10

# Final
rigidbody_world.solver_iterations = 20
```

### 4. Deactivate Distant Objects

```python
# Objects far from action can sleep
obj.rigid_body.use_deactivation = True
obj.rigid_body.deactivate_linear_velocity = 0.4
obj.rigid_body.deactivate_angular_velocity = 0.5
```

---

## Kesimpulan

Anda telah belajar:

✅ **Rigid Body Physics Fundamentals**
- ACTIVE vs PASSIVE objects
- Mass, friction, restitution, damping
- Collision shapes (SPHERE, BOX, MESH)

✅ **Kinematic-Dynamic Hybrid Animation**
- Manual control dengan keyframes
- Switch ke physics simulation
- Best of both worlds

✅ **Collision Detection**
- Proper collision shapes
- Collision margins
- Substeps dan solver iterations

✅ **Physics Tuning**
- Parameter guides untuk different materials
- Troubleshooting common issues
- Performance optimization

✅ **Complete Pipeline**
- Scene setup → Physics → Animation → Baking → Render

### Next Steps

1. **Eksperimen dengan parameter**
   - Ubah mass, friction, restitution
   - Test different collision shapes
   - Try different ball speeds

2. **Add complexity**
   - Multiple balls
   - Moving obstacles
   - Ramps and slopes

3. **Visual improvements**
   - Better materials dan textures
   - Motion blur
   - Camera tracking

4. **Advanced physics**
   - Constraints (hinges, motors)
   - Soft body physics
   - Cloth simulation

---

## Referensi

- **Blender Rigid Body**: https://docs.blender.org/manual/en/latest/physics/rigid_body/
- **Collision Shapes**: https://docs.blender.org/manual/en/latest/physics/rigid_body/properties/collisions.html
- **Physics Properties**: https://docs.blender.org/manual/en/latest/physics/rigid_body/properties/dynamics.html

---

**Selamat! Anda telah membuat animasi physics yang realistis! 🎾💥**

**Tips Terakhir:**
- Physics adalah trial and error - jangan takut eksperimen!
- Bake ulang setiap kali ubah parameter
- Start simple, add complexity gradually
- Debug dengan melihat collision shapes di viewport
- Have fun with physics! 🚀
