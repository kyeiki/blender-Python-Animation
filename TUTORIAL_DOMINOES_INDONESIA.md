# Tutorial: Membuat Animasi Domino Jatuh di Blender dengan Python

## Daftar Isi
1. [Pengenalan](#pengenalan)
2. [Persiapan](#persiapan)
3. [Struktur Dasar Script](#struktur-dasar-script)
4. [Langkah 1: Membersihkan Scene](#langkah-1-membersihkan-scene)
5. [Langkah 2: Setup Scene dan Lighting](#langkah-2-setup-scene-dan-lighting)
6. [Langkah 3: Membuat Material](#langkah-3-membuat-material)
7. [Langkah 4: Membuat Ground dan Domino](#langkah-4-membuat-ground-dan-domino)
8. [Langkah 5: Setup Physics](#langkah-5-setup-physics)
9. [Langkah 6: Membuat Kamera](#langkah-6-membuat-kamera)
10. [Langkah 7: Membuat Bola Pemicu](#langkah-7-membuat-bola-pemicu)
11. [Langkah 8: Animasi Bola dan Physics](#langkah-8-animasi-bola-dan-physics)
12. [Langkah 9: Efek Partikel](#langkah-9-efek-partikel)
13. [Langkah 10: Render Setting](#langkah-10-render-setting)
14. [Tips dan Troubleshooting](#tips-dan-troubleshooting)

---

## Pengenalan

Tutorial ini akan mengajarkan Anda cara membuat animasi domino jatuh yang realistis menggunakan Blender Python API. Animasi ini menampilkan:
- 15 domino berwarna-warni yang tersusun dalam garis lurus
- Bola merah yang memicu reaksi berantai
- Kamera yang mengikuti aksi
- Efek partikel debu
- Simulasi fisika yang realistis

**Konsep Penting:**
- **Rigid Body Physics**: Simulasi fisika untuk objek padat
- **Kinematic Animation**: Kontrol animasi manual sebelum fisika aktif
- **Keyframe**: Titik-titik waktu untuk animasi
- **Materials**: Warna dan tekstur objek

---

## Persiapan

### Yang Anda Butuhkan:
1. **Blender 4.3** atau lebih baru
2. **Python** (sudah termasuk dalam Blender)
3. Text editor (bisa menggunakan text editor Blender atau eksternal)

### Cara Menjalankan Script:
1. Buka Blender
2. Buat file Python baru (`.py`)
3. Copy script ke file
4. Buka Blender, pilih **Scripting** workspace
5. Klik **Open** dan pilih file Python Anda
6. Klik **Run Script** atau tekan `Alt + P`

---

## Struktur Dasar Script

Script kita terdiri dari beberapa fungsi utama:

```python
import bpy          # Blender Python API
import math         # Untuk perhitungan matematika
import random       # Untuk variasi acak
from mathutils import Vector  # Untuk vektor 3D
```

**Penjelasan Import:**
- `bpy`: Ini adalah API utama Blender untuk Python
- `math`: Digunakan untuk perhitungan sudut, sinus, cosinus
- `random`: Membuat variasi massa domino agar lebih realistis
- `mathutils.Vector`: Menangani koordinat 3D (x, y, z)

---

## Langkah 1: Membersihkan Scene

```python
def clear_scene():
    """Clear all objects from the current scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
```

**Penjelasan:**
- `bpy.ops.object.select_all(action='SELECT')`: Pilih semua objek di scene
- `bpy.ops.object.delete(use_global=False)`: Hapus semua objek yang dipilih
- `use_global=False`: Hanya hapus di scene aktif, bukan di semua scene

**Mengapa Penting?**
Ini memastikan scene kita bersih sebelum membuat animasi baru. Tanpa ini, objek lama akan mengganggu animasi baru.

---

## Langkah 2: Setup Scene dan Lighting

```python
def setup_scene():
    """Set up basic scene properties"""
    # Set frame rate dan range animasi
    bpy.context.scene.render.fps = 24
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 180
    bpy.context.scene.frame_set(1)
```

**Penjelasan Parameter:**
- `fps = 24`: Frame per detik (standar film)
- `frame_start = 1`: Animasi mulai dari frame 1
- `frame_end = 180`: Animasi berakhir di frame 180 (7.5 detik)
- `frame_set(1)`: Set timeline ke frame 1

### Menambahkan Lighting

```python
    # Lampu Matahari (Sun Light)
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))
```

**Jenis-jenis Lampu:**
1. **SUN**: Cahaya paralel seperti matahari, menerangi semua arah sama
2. **AREA**: Cahaya area persegi, lebih soft
3. **POINT**: Cahaya dari satu titik ke segala arah
4. **SPOT**: Cahaya fokus seperti spotlight

**Tips Lighting:**
- `energy = 3.0`: Kekuatan cahaya (nilai lebih tinggi = lebih terang)
- `math.radians(45)`: Konversi 45 derajat ke radian (Blender pakai radian)

```python
    # Lampu Area 1 (dari belakang kiri)
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    area = bpy.context.active_object
    area.data.energy = 2.0
    area.data.size = 5.0
    
    # Lampu Area 2 (dari depan)
    bpy.ops.object.light_add(type='AREA', location=(0, 5, 8))
    area2 = bpy.context.active_object
    area2.data.energy = 1.5
    area2.data.size = 3.0
```

**Mengapa 3 Lampu?**
- Lampu 1 (Sun): Pencahayaan utama
- Lampu 2 (Area): Mengisi bayangan dari belakang
- Lampu 3 (Area): Pencahayaan depan agar objek tidak terlalu gelap

---

## Langkah 3: Membuat Material

### Material Dasar dengan Warna

```python
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
```

**Penjelasan Parameter Material:**
- `name`: Nama material (misal: "DominoMaterial_01")
- `color`: Warna dalam format RGBA (Red, Green, Blue, Alpha)
  - Contoh: `(1.0, 0.0, 0.0, 1.0)` = Merah penuh
  - Rentang nilai: 0.0 sampai 1.0
- `roughness`: Kekasaran permukaan (0 = mengkilap, 1 = kasar)
- `metallic`: Tingkat metalik (0 = non-metal, 1 = metal penuh)

**Principled BSDF:**
Ini adalah shader utama di Blender yang mensimulasikan berbagai jenis material (plastik, metal, kaca, dll).

### Cara Mengaplikasikan Material

```python
def apply_material(obj, material):
    """Apply material to object"""
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)
```

**Penjelasan:**
- Jika objek sudah punya material, ganti yang pertama
- Jika belum punya material, tambahkan material baru

### Material dengan Gradient

```python
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
```

**Node System di Blender:**
Material di Blender menggunakan sistem node yang saling terhubung:
1. **Texture Coordinate**: Menentukan cara tekstur dipetakan
2. **Gradient Texture**: Membuat gradasi warna
3. **Mix RGB**: Mencampur dua warna
4. **Principled BSDF**: Shader utama
5. **Material Output**: Output akhir ke objek

---

## Langkah 4: Membuat Ground dan Domino

### Membuat Ground (Lantai)

```python
def setup_domino_scene():
    """Create dominoes and ground"""
    # Membuat lantai DATAR
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground.rotation_euler = (0, 0, 0)  # Pastikan lantai rata sempurna
```

**Penjelasan:**
- `primitive_plane_add`: Menambahkan plane (persegi datar)
- `size=20`: Ukuran 20 unit Blender (cukup besar untuk semua domino)
- `location=(0, 0, 0)`: Di titik tengah dunia
- `rotation_euler=(0, 0, 0)`: Tidak ada rotasi = lantai sempurna rata

**Mengapa Lantai Harus Rata?**
Jika lantai miring sedikit saja, domino akan jatuh sendiri sebelum bola mengenainya!

### Membuat Material Ground

```python
    # Membuat material gradient untuk ground
    try:
        ground_mat = create_textured_material("GroundMaterial", "//wood_texture.jpg")
    except:
        ground_mat = create_gradient_material("GroundMaterial", 
                                            (0.15, 0.1, 0.05, 1.0),    # Warna coklat gelap
                                            (0.25, 0.15, 0.1, 1.0))    # Warna coklat terang
        ground_mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.8
    apply_material(ground, ground_mat)
```

**Penjelasan Try-Except:**
- `try`: Coba load tekstur kayu dari file
- `except`: Jika gagal, gunakan gradient sebagai fallback
- `Roughness = 0.8`: Lantai kasar (tidak mengkilap)

### Membuat Domino dalam Loop

```python
    # Setup parameter domino
    dominoes = []
    domino_width = 0.3      # Lebar (X)
    domino_height = 2.0     # Tinggi (Z)
    domino_depth = 0.8      # Kedalaman (Y)
    spacing = 0.65          # Jarak antar domino
    num_dominoes = 15       # Jumlah domino
```

**Proporsi Domino:**
- Tipis (width = 0.3)
- Tinggi (height = 2.0)
- Sedang (depth = 0.8)
- Spacing = 0.65: Cukup dekat untuk saling mendorong, tapi tidak tumpang tindih

```python
    for i in range(num_dominoes):
        # Hitung posisi X (garis lurus)
        x_pos = -5 + i * spacing
        y_pos = 0  # Garis lurus, tidak melengkung
        
        # Buat kubus
        bpy.ops.mesh.primitive_cube_add(
            size=1,  # Kubus unit 1x1x1
            location=(x_pos, y_pos, domino_height/2)
        )
        domino = bpy.context.active_object
        domino.name = f"Domino_{i:02d}"
```

**Penjelasan Posisi:**
- `x_pos = -5 + i * spacing`: 
  - Domino 0: x = -5
  - Domino 1: x = -5 + 0.65 = -4.35
  - Domino 2: x = -5 + 1.3 = -3.7
  - dst...
- `domino_height/2`: Setengah tinggi agar dasar domino tepat di Z=0
- `f"Domino_{i:02d}"`: Nama dengan format "Domino_00", "Domino_01", dll

```python
        # Scale kubus menjadi proporsi domino
        domino.scale = (domino_width, domino_depth, domino_height)
        
        # Tidak perlu rotasi karena garis lurus
        domino.rotation_euler = (0, 0, 0)
```

**Scale vs Size:**
- Kita buat kubus ukuran 1x1x1 dulu
- Lalu scale dengan proporsi domino
- Ini lebih mudah daripada menghitung size langsung

### Membuat Warna Pelangi untuk Domino

```python
        # Buat warna pelangi dengan formula matematika
        hue = i / num_dominoes  # Nilai 0 sampai 1
        color = (
            0.5 + 0.5 * math.cos(hue * 2 * math.pi),
            0.5 + 0.5 * math.cos(hue * 2 * math.pi + 2*math.pi/3),
            0.5 + 0.5 * math.cos(hue * 2 * math.pi + 4*math.pi/3),
            1.0
        )
        
        domino_mat = create_material(f"DominoMaterial_{i:02d}", color, 
                                    roughness=0.3, metallic=0.1)
        apply_material(domino, domino_mat)
        
        dominoes.append(domino)
```

**Formula Warna Pelangi:**
- Menggunakan fungsi cosinus untuk membuat gradasi halus
- `hue * 2 * math.pi`: Satu putaran penuh lingkaran warna
- `2*math.pi/3` dan `4*math.pi/3`: Offset untuk RGB
- Hasil: Transisi merah → kuning → hijau → biru → ungu

**Properti Material Domino:**
- `roughness=0.3`: Agak mengkilap (seperti plastik)
- `metallic=0.1`: Sedikit efek metalik

---

## Langkah 5: Setup Physics

### Rigid Body Physics untuk Domino

```python
def setup_physics(dominoes, ground):
    """Set up rigid body physics for all objects"""
    # Tambahkan physics ke semua domino
    for i, domino in enumerate(dominoes):
        bpy.context.view_layer.objects.active = domino
        bpy.ops.rigidbody.object_add()
        domino.rigid_body.type = 'ACTIVE'
```

**Jenis Rigid Body:**
- **ACTIVE**: Objek yang dipengaruhi gravitasi dan collision (domino, bola)
- **PASSIVE**: Objek statis yang tidak bergerak tapi bisa ditabrak (ground, dinding)
- **ANIMATED**: Objek yang dianimasi manual tapi masih bisa collision

```python
        domino.rigid_body.mass = 0.5
        domino.rigid_body.friction = 0.4
        domino.rigid_body.restitution = 0.1
        domino.rigid_body.linear_damping = 0.1
        domino.rigid_body.angular_damping = 0.1
```

**Parameter Physics:**
- `mass = 0.5`: Massa 0.5 kg (ringan tapi tidak terlalu)
- `friction = 0.4`: Gesekan sedang (tidak licin, tidak lengket)
- `restitution = 0.1`: Pantulan rendah (hampir tidak memantul)
- `linear_damping = 0.1`: Redaman gerakan linear (seperti hambatan udara)
- `angular_damping = 0.1`: Redaman rotasi

**Mengapa Nilai-nilai Ini?**
- Massa rendah: Domino mudah jatuh
- Friction sedang: Domino tidak slip tapi bisa slide
- Restitution rendah: Domino tidak memantul (realistis)
- Damping rendah: Gerakan natural tanpa terlalu banyak hambatan

```python
        # Variasi massa untuk dinamika lebih menarik
        domino.rigid_body.mass = 0.4 + random.random() * 0.2
```

**Random Variation:**
- `random.random()`: Nilai acak 0.0 sampai 1.0
- `0.4 + random.random() * 0.2`: Massa antara 0.4 kg sampai 0.6 kg
- Variasi kecil ini membuat gerakan lebih natural dan tidak terlalu sempurna

### Physics untuk Ground

```python
    # Tambahkan physics ke ground
    bpy.context.view_layer.objects.active = ground
    bpy.ops.rigidbody.object_add()
    ground.rigid_body.type = 'PASSIVE'
    ground.rigid_body.friction = 0.8
```

**Ground Settings:**
- `type = 'PASSIVE'`: Ground tidak bergerak
- `friction = 0.8`: Friction tinggi agar domino tidak slip

---

## Langkah 6: Membuat Kamera

```python
def setup_camera():
    """Set up animated camera for dynamic viewing"""
    bpy.ops.object.camera_add(location=(0, -12, 6))
    camera = bpy.context.active_object
    camera.name = "AnimationCamera"
    bpy.context.scene.camera = camera
```

**Setup Kamera:**
- `location=(0, -12, 6)`: Posisi awal di belakang dan atas
- `bpy.context.scene.camera = camera`: Set sebagai kamera aktif untuk render

### Animasi Kamera dengan Keyframe

```python
    # Keyframe 1: Posisi awal (frame 1)
    bpy.context.scene.frame_set(1)
    camera.location = (-6, -10, 5)
    camera.rotation_euler = (math.radians(65), 0, math.radians(10))
    camera.keyframe_insert(data_path="location", frame=1)
    camera.keyframe_insert(data_path="rotation_euler", frame=1)
```

**Sistem Keyframe:**
1. Set frame timeline ke posisi tertentu
2. Set properti objek (location, rotation)
3. Insert keyframe untuk menyimpan nilai di frame tersebut
4. Blender akan interpolasi otomatis antara keyframe

**Posisi Keyframe:**
- Frame 1: Kamera kiri (-6, -10, 5), lihat ke kanan bawah
- Frame 60: Kamera agak tengah (-2, -12, 6)
- Frame 120: Kamera agak kanan (2, -12, 6)
- Frame 180: Kamera kanan (6, -10, 5), lihat ke kiri bawah

**Rotasi Kamera:**
- `math.radians(65)`: Pitch 65° (melihat ke bawah)
- `0`: Roll 0° (tidak miring)
- `math.radians(10)` atau `math.radians(-10)`: Yaw (mengikuti arah domino)

**Hasil Animasi Kamera:**
Kamera bergerak dari kiri ke kanan mengikuti domino yang jatuh, menciptakan tracking shot yang smooth.

---

## Langkah 7: Membuat Bola Pemicu

```python
def create_trigger_ball():
    """Create a ball to trigger the first domino"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(-10, 0, 3))
    ball = bpy.context.active_object
    ball.name = "TriggerBall"
```

**Properti Bola:**
- `radius=0.5`: Ukuran sedang (diameter 1 unit)
- `location=(-10, 0, 3)`: Mulai dari kiri, di atas
- UV Sphere: Bola dengan segmen yang merata (bagus untuk rendering)

### Material Bola

```python
    # Material merah mengkilap
    ball_mat = create_material("TriggerBallMaterial", (0.8, 0.2, 0.2, 1.0), 
                              roughness=0.1, metallic=0.3)
    apply_material(ball, ball_mat)
```

**Warna Merah:**
- `(0.8, 0.2, 0.2, 1.0)`: Merah terang
- `roughness=0.1`: Sangat mengkilap (seperti bola biliar)
- `metallic=0.3`: Sedikit efek metalik

### Physics Bola

```python
    # Tambahkan physics dengan massa tinggi
    bpy.ops.rigidbody.object_add()
    ball.rigid_body.type = 'ACTIVE'
    ball.rigid_body.mass = 2.0  # Massa tinggi untuk impact kuat
    ball.rigid_body.friction = 0.4
    ball.rigid_body.restitution = 0.5
    ball.rigid_body.kinematic = True  # Mulai dengan kontrol manual
```

**Parameter Bola:**
- `mass = 2.0`: 4x lebih berat dari domino (impact lebih kuat)
- `friction = 0.4`: Gesekan sedang
- `restitution = 0.5`: Pantulan sedang (bola bisa memantul sedikit)
- `kinematic = True`: **Penting!** Bola dikontrol animasi dulu, bukan physics

**Kinematic vs Dynamic:**
- **Kinematic**: Objek bergerak sesuai keyframe animation (tidak terpengaruh gravitasi)
- **Dynamic**: Objek bergerak sesuai physics simulation (terpengaruh gravitasi)
- Kita mulai kinematic, lalu switch ke dynamic di tengah animasi

---

## Langkah 8: Animasi Bola dan Physics

### Strategi Hybrid: Kinematic → Dynamic

```python
def animate_falling_dominoes():
    # ... setup objek ...
    
    # Dapatkan posisi domino pertama
    first_domino = dominoes[0]
    domino_x = first_domino.location.x
    domino_y = first_domino.location.y
```

**Mengapa Butuh Posisi Domino?**
Kita ingin bola mengenai domino pertama dengan akurat, jadi kita hitung posisinya terlebih dahulu.

### Animasi Kinematic (Frame 1-25)

```python
    # Set kinematic aktif
    trigger_ball.rigid_body.kinematic = True
    
    # Keyframe 1: Posisi awal
    bpy.context.scene.frame_set(1)
    trigger_ball.location = (domino_x - 3.0, domino_y, 1.0)
    trigger_ball.keyframe_insert(data_path="location", frame=1)
    trigger_ball.rigid_body.keyframe_insert("kinematic", frame=1)
```

**Posisi Awal Bola:**
- `domino_x - 3.0`: 3 unit di kiri domino pertama
- `domino_y`: Sama dengan Y domino (segaris)
- `1.0`: Ketinggian 1 unit (setinggi tengah domino)

```python
    # Keyframe 25: Bola mendekati domino
    bpy.context.scene.frame_set(25)
    trigger_ball.location = (domino_x - 0.6, domino_y, 1.0)
    trigger_ball.keyframe_insert(data_path="location", frame=25)
    trigger_ball.rigid_body.keyframe_insert("kinematic", frame=25)
```

**Gerakan Horizontal:**
- Bola bergerak dari `domino_x - 3.0` ke `domino_x - 0.6`
- Jarak: 2.4 unit dalam 24 frame (1 detik pada 24fps)
- **Tidak ada gerakan vertikal**: Z tetap 1.0 (tidak jatuh karena masih kinematic)

### Switch ke Dynamic Physics (Frame 26+)

```python
    # Frame 26: Switch ke physics simulation
    bpy.context.scene.frame_set(26)
    trigger_ball.rigid_body.kinematic = False
    trigger_ball.rigid_body.keyframe_insert("kinematic", frame=26)
```

**Momen Kritis:**
- Frame 1-25: Bola bergerak horizontal dengan animasi manual
- Frame 26: `kinematic = False` → Bola sekarang mengikuti physics
- Frame 26+: Gravitasi aktif, bola bisa collision dengan domino

**Mengapa Strategi Ini?**
1. **Kontrol Presisi**: Kita pastikan bola mengenai domino dengan tepat
2. **Natural Transition**: Bola sudah punya momentum horizontal ketika physics aktif
3. **Reliable Impact**: Tidak bergantung pada perhitungan trajectory yang rumit

### Setup Rigid Body World

```python
    # Buat rigid body world jika belum ada
    if not bpy.context.scene.rigidbody_world:
        bpy.ops.rigidbody.world_add()
    
    rigidbody_world = bpy.context.scene.rigidbody_world
```

**Rigid Body World:**
Ini adalah sistem yang mengelola semua objek physics di scene.

```python
    # Tambahkan objek ke rigid body world (dengan safety check)
    if trigger_ball.name not in rigidbody_world.collection.objects:
        rigidbody_world.collection.objects.link(trigger_ball)
    for domino in dominoes:
        if domino.name not in rigidbody_world.collection.objects:
            rigidbody_world.collection.objects.link(domino)
    if ground.name not in rigidbody_world.collection.objects:
        rigidbody_world.collection.objects.link(ground)
```

**Safety Check:**
Kita cek apakah objek sudah ada di collection sebelum menambahkan. Ini mencegah error "already in collection" jika script dijalankan ulang.

### Konfigurasi Physics Simulation

```python
    # Set range simulation
    rigidbody_world.point_cache.frame_start = 1
    rigidbody_world.point_cache.frame_end = 180
    
    # Substeps untuk akurasi (Blender 4.3+)
    rigidbody_world.substeps_per_frame = 10
    rigidbody_world.solver_iterations = 20
```

**Parameter Simulasi:**
- `substeps_per_frame = 10`: Hitung physics 10x per frame
  - Frame rate: 24 fps
  - Physics rate: 24 × 10 = 240 simulasi per detik
  - Hasil: Collision detection lebih akurat
  
- `solver_iterations = 20`: Solver mencoba 20x per substep
  - Lebih tinggi = lebih stabil tapi lebih lambat
  - 20 adalah sweet spot untuk domino

**Mengapa Butuh Substeps Tinggi?**
Domino tipis dan bergerak cepat. Tanpa substeps tinggi, collision bisa terlewat (objek "tembus" satu sama lain).

### Bake Physics

```python
    # Bake physics simulation
    print("Baking physics simulation...")
    bpy.context.scene.frame_set(1)
    bpy.ops.ptcache.bake_all(bake=True)
```

**Baking:**
- Menghitung dan menyimpan semua posisi physics untuk setiap frame
- Setelah di-bake, animasi bisa diputar secara real-time
- Tanpa bake, Blender harus menghitung ulang physics setiap kali play

---

## Langkah 9: Efek Partikel

```python
def add_particle_effects():
    """Add particle effects for more visual interest"""
    # Buat plane untuk emitter partikel
    bpy.ops.mesh.primitive_plane_add(size=15, location=(0, 0, 0.01))
    dust_plane = bpy.context.active_object
    dust_plane.name = "DustPlane"
    
    # Sembunyikan plane dari render (hanya partikelnya yang terlihat)
    dust_plane.hide_render = True
```

**Particle Emitter:**
- Plane berukuran 15×15 unit
- Z = 0.01: Sedikit di atas ground agar tidak overlap
- `hide_render = True`: Plane tidak terlihat di render final

### Konfigurasi Particle System

```python
    # Tambahkan particle system
    bpy.ops.object.particle_system_add()
    particle_system = dust_plane.particle_systems[0]
    settings = particle_system.settings
    
    # Konfigurasi partikel (Blender 4.3+)
    settings.type = 'EMITTER'
    settings.emit_from = 'FACE'
    settings.count = 500
    settings.frame_start = 20
    settings.frame_end = 150
    settings.lifetime = 50
```

**Parameter Partikel:**
- `type = 'EMITTER'`: Emit partikel dari mesh
- `emit_from = 'FACE'`: Emit dari permukaan face
- `count = 500`: Total 500 partikel
- `frame_start = 20`: Mulai emit frame 20 (setelah bola bergerak)
- `frame_end = 150`: Stop emit frame 150
- `lifetime = 50`: Setiap partikel hidup 50 frame (~2 detik)

```python
    settings.normal_factor = 0.1
    settings.factor_random = 0.5
    settings.angular_velocity_factor = 0.5
    settings.use_rotations = True
    settings.rotation_factor_random = 1.0
```

**Gerakan Partikel:**
- `normal_factor = 0.1`: Emit sedikit ke atas (mengikuti normal face)
- `factor_random = 0.5`: Randomisasi kecepatan 50%
- `angular_velocity_factor = 0.5`: Partikel berputar
- `rotation_factor_random = 1.0`: Rotasi random 100%

```python
    # Physics partikel
    settings.physics_type = 'NEWTON'
    settings.factor_random = 0.5
    
    # Ukuran partikel debu kecil
    settings.particle_size = 0.02
    settings.size_random = 0.5
```

**Ukuran Partikel:**
- `particle_size = 0.02`: Partikel sangat kecil (seperti debu)
- `size_random = 0.5`: Variasi ukuran 50%

### Material Partikel

```python
    # Material debu semi-transparan
    dust_mat = create_material("DustMaterial", (0.6, 0.5, 0.4, 0.5))
    dust_mat.blend_method = 'BLEND'
    apply_material(dust_plane, dust_mat)
```

**Warna Debu:**
- `(0.6, 0.5, 0.4, 0.5)`: Warna coklat muda, alpha 0.5 (semi-transparan)
- `blend_method = 'BLEND'`: Mode blending untuk transparansi

---

## Langkah 10: Render Setting

```python
def setup_render_settings():
    """Configure render settings for output"""
    # Set render engine
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
```

**Render Engine:**
- **CYCLES**: Engine yang lebih realistis (ray tracing)
- **EEVEE**: Engine real-time (lebih cepat tapi kurang realistis)
- `device = 'GPU'`: Gunakan GPU untuk render lebih cepat

### Output Video Format

```python
    # Set format output
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
```

**Video Encoding:**
- `FFMPEG`: Library untuk video encoding
- `MPEG4`: Container format (seperti MP4)
- `H264`: Codec video (standar untuk web)
- `constant_rate_factor = 'MEDIUM'`: Kualitas sedang (balance size/quality)

### Resolusi dan Kualitas

```python
    # Resolusi Full HD
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 100
    
    # Samples untuk kualitas
    bpy.context.scene.cycles.samples = 128
```

**Resolusi:**
- 1920×1080: Full HD (standar YouTube)
- `resolution_percentage = 100`: Render di full resolution

**Samples:**
- Samples = jumlah ray tracing per pixel
- 128 samples: Kualitas bagus dengan noise minimal
- Lebih tinggi = lebih smooth tapi render lebih lama

### Motion Blur

```python
    # Motion blur untuk kualitas animasi lebih baik
    bpy.context.scene.render.use_motion_blur = True
    bpy.context.scene.cycles.motion_blur_samples = 8
```

**Motion Blur:**
- Membuat gerakan cepat terlihat lebih smooth
- `samples = 8`: Kualitas motion blur

### Output Path

```python
    # Set output path (absolute path)
    import os
    output_dir = r"F:\blender2025\pertemuan3"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    bpy.context.scene.render.filepath = os.path.join(output_dir, "falling_dominoes_animation.mp4")
```

**Path Management:**
- Gunakan absolute path untuk menghindari error
- Create directory jika belum ada
- Output: `F:\blender2025\pertemuan3\falling_dominoes_animation.mp4`

---

## Tips dan Troubleshooting

### Tips Optimasi

1. **Kurangi Jumlah Domino:**
   ```python
   num_dominoes = 10  # Dari 15 jadi 10 untuk test
   ```

2. **Render Test dengan Resolusi Rendah:**
   ```python
   bpy.context.scene.render.resolution_percentage = 50  # 50% resolution
   bpy.context.scene.cycles.samples = 64  # Samples lebih rendah
   ```

3. **Skip Particle untuk Test:**
   Komen baris ini di `animate_falling_dominoes()`:
   ```python
   # add_particle_effects()
   ```

### Troubleshooting Common Issues

#### 1. **Domino Jatuh Sendiri Sebelum Bola Datang**

**Penyebab:** Lantai tidak rata atau domino overlap

**Solusi:**
```python
# Pastikan ground rotation = 0
ground.rotation_euler = (0, 0, 0)

# Tambahkan jarak spacing
spacing = 0.7  # Dari 0.65 jadi 0.7
```

#### 2. **Bola Tidak Mengenai Domino**

**Penyebab:** Posisi bola tidak akurat

**Solusi:**
```python
# Tambahkan debug print
print(f"Domino position: {domino_x}, {domino_y}")
print(f"Ball target: {domino_x - 0.6}, {domino_y}")
```

#### 3. **Domino Tembus Satu Sama Lain**

**Penyebab:** Substeps terlalu rendah

**Solusi:**
```python
rigidbody_world.substeps_per_frame = 20  # Dari 10 jadi 20
rigidbody_world.solver_iterations = 30   # Dari 20 jadi 30
```

#### 4. **Error: 'RigidBodyWorld' object has no attribute 'steps_per_second'**

**Penyebab:** Menggunakan API lama di Blender 4.3+

**Solusi:** Gunakan `substeps_per_frame` bukan `steps_per_second`

#### 5. **Error: "already in collection"**

**Penyebab:** Script dijalankan 2x tanpa clear scene

**Solusi:** Sudah ada safety check di code kita:
```python
if trigger_ball.name not in rigidbody_world.collection.objects:
    rigidbody_world.collection.objects.link(trigger_ball)
```

#### 6. **Partikel Tidak Muncul**

**Penyebab:** Particle type salah

**Solusi:** Gunakan `'EMITTER'` bukan `'EMIT'` (Blender 4.3+)

### Performance Tips

1. **Bake Physics Sebelum Render:**
   - Physics sudah di-bake otomatis di script
   - Jika render lambat, bake lagi manual: `Ctrl + B` di timeline

2. **Gunakan Viewport Shading untuk Preview:**
   - Tekan `Z` → pilih "Solid" atau "Material Preview"
   - Jangan langsung render, test dulu di viewport

3. **Render Frame Tertentu Saja:**
   ```python
   bpy.context.scene.frame_start = 20
   bpy.context.scene.frame_end = 40
   ```

### Customization Ideas

#### 1. **Domino Melengkung**

```python
# Ubah bagian ini di setup_domino_scene():
for i in range(num_dominoes):
    x_pos = -5 + i * spacing
    # Tambahkan curve dengan sinus
    y_pos = 2 * math.sin(i * 0.3)  # Curve halus
    
    # Hitung angle untuk rotasi
    angle = math.atan2(
        2 * math.sin((i+1) * 0.3) - y_pos,
        spacing
    )
    domino.rotation_euler = (0, 0, angle)
```

#### 2. **Warna Custom**

```python
# Warna semua domino biru:
color = (0.2, 0.4, 0.9, 1.0)  # Biru

# Atau gradient dari merah ke biru:
t = i / num_dominoes
color = (
    1.0 - t,  # Red menurun
    0.0,
    t,        # Blue meningkat
    1.0
)
```

#### 3. **Lebih Banyak Bola**

```python
# Buat 3 bola dengan delay berbeda
for ball_idx in range(3):
    ball = create_trigger_ball()
    ball.name = f"Ball_{ball_idx}"
    
    # Posisi berbeda
    ball.location.y = -2 + ball_idx * 2
    
    # Delay berbeda
    start_frame = 1 + ball_idx * 30
    end_frame = start_frame + 24
    # ... setup keyframes dengan frame berbeda
```

#### 4. **Kamera POV (First Person)**

```python
# Kamera mengikuti bola
def setup_camera():
    # ... camera setup ...
    
    # Tambahkan constraint
    bpy.ops.object.constraint_add(type='TRACK_TO')
    constraint = camera.constraints[-1]
    constraint.target = trigger_ball
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
```

---

## Kesimpulan

Anda telah belajar:

✅ **Dasar-dasar Blender Python API**
- Import dan penggunaan `bpy`
- Manipulasi objek 3D
- Material dan node system

✅ **Rigid Body Physics**
- Setup ACTIVE dan PASSIVE objects
- Parameter mass, friction, restitution
- Substeps dan solver iterations

✅ **Animasi dengan Keyframe**
- Insert keyframe untuk location dan rotation
- Interpolasi otomatis antara keyframe
- Animasi kamera tracking

✅ **Strategi Kinematic-Dynamic Hybrid**
- Kontrol presisi dengan kinematic
- Transition ke dynamic physics
- Reliable collision dan impact

✅ **Particle System**
- Setup emitter
- Konfigurasi lifetime dan velocity
- Material transparan untuk efek debu

✅ **Render Pipeline**
- Cycles vs EEVEE
- Output video dengan FFMPEG
- Optimasi samples dan resolution

### Latihan Lanjutan

1. **Buat variasi domino berbeda:**
   - Domino berbentuk silinder
   - Domino dengan pattern warna custom
   - Domino dengan tekstur gambar

2. **Tambahkan elemen interaktif:**
   - Obstacle di tengah jalur domino
   - Ramp untuk domino melompat
   - Trigger berbeda (bukan bola)

3. **Eksperimen dengan physics:**
   - Ubah massa untuk efek berbeda
   - Tambahkan force field (angin)
   - Slow motion dengan time remapping

4. **Improve visual effects:**
   - Tambahkan shadow yang lebih dramatis
   - HDR lighting untuk refleksi
   - Depth of field untuk blur background

---

## Referensi

- **Blender Python API Docs**: https://docs.blender.org/api/current/
- **Rigid Body Physics**: https://docs.blender.org/manual/en/latest/physics/rigid_body/
- **Particle System**: https://docs.blender.org/manual/en/latest/physics/particles/
- **Cycles Render**: https://docs.blender.org/manual/en/latest/render/cycles/

---

**Selamat belajar! Semoga tutorial ini membantu Anda memahami cara membuat animasi domino jatuh dengan Blender Python. 🎉**

**Jangan lupa:**
- Save script Anda secara berkala
- Test dengan parameter kecil dulu sebelum render final
- Eksperimen dengan nilai-nilai untuk memahami efeknya
- Have fun! 🚀
