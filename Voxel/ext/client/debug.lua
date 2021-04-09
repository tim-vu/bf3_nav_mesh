require('voxelizer')
require('constants')

local STEP_SIZE = Vec3(0.3, 0.3, 0.3)
local ITERS_PER_TICK = 10

local aabb = nil

local bbGrid = nil

local performVoxelization = false
local performRaycastTest = false
local voxelizer = nil

local position = nil
local trans = nil

DebugGUI:Folder('Debug', function()

  DebugGUI:Button('Clear voxelization', function()
    voxelizer = nil
    performVoxelization = false
  end)

  DebugGUI:Button('Voxelize', function()

    local player = PlayerManager:GetLocalPlayer()

    if not player.soldier or not player.soldier.isAlive then
      return
    end

    local position = player.soldier.transform.trans

    local chunkX = position.x // CHUNK_SIZE
    local chunkZ = position.z // CHUNK_SIZE

    voxelizer = Voxelizer(AxisAlignedBox(Vec3(chunkX * CHUNK_SIZE, MIN_Y, chunkZ * CHUNK_SIZE), Vec3((chunkX + 1) * CHUNK_SIZE, MAX_Y, (chunkZ + 1) * CHUNK_SIZE)), STEP_SIZE, math.rad(50), ITERS_PER_TICK)
    bbGrid = voxelizer:createBoundingBoxMatrix()

    performVoxelization = true
  end)

end)

Events:Subscribe('UpdateManager:Update', function(deltaTime, updatePass)

  if updatePass ~= UpdatePass.UpdatePass_PreSim then
    return
  end

  if performRaycastTest then

    local dir = Vec3(0, -1, 0)

    local hit = RaycastManager:Raycast(position, position + dir, RayCastFlags.DontCheckCharacter | RayCastFlags.DontCheckWater | RayCastFlags.CheckDetailMesh)

    performRaycastTest = false
    if not hit then
      print('No hit')
      return
    end

    print(string.format('Normal: %s', hit.normal))

    print(string.format('Pi sin: %f', math.sin(math.pi)))

    local frac = math.abs(hit.normal.x) / (math.sqrt(hit.normal.x^2 + hit.normal.y^2 + hit.normal.z^2))
    print(string.format('sin: %f', math.sin(frac)))

    print(string.format('Angle: %f', math.deg(math.asin(frac))))

  end

  if performVoxelization then
    local done = voxelizer:voxelize(aabb, STEP_SIZE, ITERS_PER_TICK)

    if done then
      performVoxelization = false
    end

    return
  end

end)

Events:Subscribe('Client:UpdateInput', function(deltaTime)

  if InputManager:WentKeyDown(InputDeviceKeys.IDK_F) then

    local transform = ClientUtils:GetCameraTransform()
    local direction = Vec3(-transform.forward.x, -transform.forward.y, -transform.forward.z)

    local castStart = transform.trans
    local castEnd = Vec3(
      transform.trans.x + (direction.x * 100),
      transform.trans.y + (direction.y * 100),
      transform.trans.z + (direction.z * 100)
    )

    local hit = RaycastManager:Raycast(castStart, castEnd,
      RayCastFlags.DontCheckWater |
      RayCastFlags.DontCheckCharacter |
      RayCastFlags.DontCheckRagdoll |
      RayCastFlags.CheckDetailMesh
    )

    if not hit then
      return
    end

    NetEvents:Send('Setup:Teleport', hit.position)
  end

  if InputManager:WentKeyDown(InputDeviceKeys.IDK_G) then

    local transform = ClientUtils:GetCameraTransform()
    local direction = Vec3(-transform.forward.x, -transform.forward.y, -transform.forward.z)

    local castStart = transform.trans
    local castEnd = Vec3(
      transform.trans.x + (direction.x * 100),
      transform.trans.y + (direction.y * 100),
      transform.trans.z + (direction.z * 100)
    )

    local hit = RaycastManager:Raycast(castStart, castEnd,
      RayCastFlags.DontCheckWater |
      RayCastFlags.DontCheckCharacter |
      RayCastFlags.DontCheckRagdoll |
      RayCastFlags.CheckDetailMesh
    )

    position = hit.position

    local normal = hit.normal

    local value = 0

    print(string.format('Dot product: %f', normal:Dot(Vec3.up)))
    print(string.format('Cos: %f', math.cos(math.rad(50))))

    if math.cos(math.rad(55)) < normal:Dot(Vec3.up) then
      value = 1
    else
      value = 2
    end


    print(string.format('Normal: %s', normal))
    print(string.format('Value: %f', value))

  end

end)

Console:Register('test', '', function()

  local stepSize = Vec3(0.2, 0.24, 0.2)
  local size = Vec3(25, 125, 25)

  local steps = Vec3(
    size.x // stepSize.x,
    size.y // stepSize.y,
    size.z // stepSize.z
  )

  print(size.x)
  print(stepSize.x)
  print('5.000000 // 0.200000 = ' .. tostring(5.000000 // 0.200000))
  print(size.x // stepSize.x)
  print('Size: '  .. tostring(size))
  print('Stepsize: ' .. tostring(stepSize))
  print('Steps: ' .. tostring(steps))

end)

Events:Subscribe('FPSCamera:Update', function(deltaTime)

  local player = PlayerManager:GetLocalPlayer()

  if not player.soldier or not player.soldier.isAlive then
    return
  end

  if voxelizer and bbGrid then
    for x = 1, #voxelizer.grid do
      for z = 1, #voxelizer.grid[1][1] do

        for y = 1, #voxelizer.grid[1] do

          if voxelizer.grid[x][y][z] == 1 then
            DebugRenderer:DrawOBB(bbGrid[x][y][z], LinearTransform(), Vec4(0, 255, 0, 1))
          elseif voxelizer.grid[x][y][z] == 2 then
            DebugRenderer:DrawOBB(bbGrid[x][y][z], LinearTransform(), Vec4(255, 0, 0, 1))
          end

        end
      end
    end
  end

  if position then
    DebugRenderer:DrawSphere(position, 0.2, Vec4(255, 0, 0, 1), false, false)
  end

end)