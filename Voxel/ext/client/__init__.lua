require('__shared/debug-gui')
require('constants')

require('debug')
require('level-scanner')

local levelId = 1
local areaPoints = {Vec3(-403.739044, 72.280411, 235.388123), Vec3(-399.897736, 72.280411, 205.014771), Vec3(-377.219147, 72.280411, 177.341385), Vec3(-360.497528, 72.280411, 178.590790), Vec3(-352.627930, 72.280411, 175.884872), Vec3(-349.914246, 72.280411, 177.527527), Vec3(-336.174896, 72.280411, 174.875397), Vec3(-334.356903, 72.280411, 173.606827), Vec3(-328.347198, 72.280411, 179.981262), Vec3(-322.246216, 72.280411, 186.003876), Vec3(-301.480743, 72.280411, 207.734344), Vec3(-296.021332, 72.280411, 226.468765), Vec3(-296.071320, 72.280411, 228.654663), Vec3(-292.396698, 72.280411, 228.516022), Vec3(-292.316315, 72.280411, 229.627808), Vec3(-291.475586, 72.280411, 231.366302), Vec3(-285.431915, 72.280411, 237.604523), Vec3(-281.443268, 72.280411, 237.536285), Vec3(-247.419052, 72.280411, 271.613037), Vec3(-330.178314, 72.280411, 352.172913), Vec3(-425.515045, 72.280411, 256.816650), Vec3(-416.125885, 72.280411, 246.396957)}
local levelScanner = nil

DebugGUI:Folder('LevelScanner', function()

  DebugGUI:Number('Level id', levelId, function(value)
    print('Level id: ' .. value)
    levelId = value
  end)

  Console:Register('set_level_id', 'Sets the levelId', function(args)

    if #args ~= 1 then
      return
    end

    local value = tonumber(args[1])

    if not value or value <= 0 then
      return
    end

    levelId = value
    print('Level id: ' .. value)

  end)

  DebugGUI:Button('Add area point', function()

    local player = PlayerManager:GetLocalPlayer()

    if not player.soldier or not player.soldier.isAlive then
      return
    end

    table.insert(areaPoints, player.soldier.transform.trans:Clone())

  end)

  DebugGUI:Button('Remove last area point', function()
    table.remove(areaPoints, #areaPoints)
  end)

  DebugGUI:Button('Clear area points', function()
    areaPoints = {}
  end)

  DebugGUI:Button('Scan current chunk', function()

    local player = PlayerManager:GetLocalPlayer()

    if not player.soldier or not player.soldier.isAlive then
      return
    end

    local position = player.soldier.transform.trans

    local chunkX = position.x // CHUNK_SIZE
    local chunkZ = position.z // CHUNK_SIZE

    local points = {
      Vec3(chunkX * CHUNK_SIZE, 70, chunkZ * CHUNK_SIZE),
      Vec3(chunkX * CHUNK_SIZE, 70, (chunkZ + 1) * CHUNK_SIZE),
      Vec3((chunkX + 1) * CHUNK_SIZE, 70, (chunkZ + 1) * CHUNK_SIZE),
      Vec3((chunkX + 1) * CHUNK_SIZE, 70, chunkZ * CHUNK_SIZE)
    }

    local area = {}

    for _, v in pairs(points) do
      table.insert(area, Vec2(v.x, v.z))
    end

    levelScanner = LevelScanner(levelId, area)
    levelScanner:startScanning()

  end)

  Console:Register('scan_level', '', function()

    if levelScanner ~= nil and not levelScanner:isDone() then
      print('A level scan is already in progress')
    end

    if #areaPoints < 3 then
      print('At least 3 points must be added')
    end

    local area = {}

    for _, v in pairs(areaPoints) do
      table.insert(area, Vec2(v.x, v.z))
    end

    levelScanner = LevelScanner(levelId, area, ChunkType.NormalBased)
    levelScanner:startScanning()

  end)

  Console:Register('stop_scan', '', function()

    if not levelScanner or not levelScanner:isRunning() then
      print('There is currently no level scan in progress')
    end

    levelScanner:stopScanning()
    levelScanner = nil

  end)

  Console:Register('position', 'Prints the local player\'s position', function()

    local player = PlayerManager:GetLocalPlayer()

    if not player.soldier or not player.soldier.isAlive then
      return
    end

    return tostring(player.soldier.transform.trans)

  end)

end)

local GREEN = Vec4(0, 255, 0, 1)
local TEXT_X = 5
local TEXT_Y = 20
local TEXT_Y_STEP = 15

local MILLISECONDS_IN_HOUR = 1000 * 60 * 60
local MILLISECONDS_IN_MINUTE = 1000 * 60
local MILLISECONDS_IN_SECOND = 1000

local function formatTime(ms)

  local hours = ms // MILLISECONDS_IN_HOUR
  ms = ms % MILLISECONDS_IN_HOUR
  local minutes = ms // MILLISECONDS_IN_MINUTE
  ms = ms % MILLISECONDS_IN_MINUTE
  local seconds = ms // MILLISECONDS_IN_SECOND

  return string.format('%02d:%02d:%02d', hours, minutes, seconds)

end

Events:Subscribe('FPSCamera:Update', function(deltaTime)

  for _, v in pairs(areaPoints) do
    DebugRenderer:DrawSphere(v, 0.3, GREEN, false, false)
  end

  if #areaPoints > 1 then

    for i = 1, #areaPoints - 1 do
      DebugRenderer:DrawLine(areaPoints[i], areaPoints[i + 1], GREEN, GREEN)
    end

  end

  if #areaPoints > 2 then
    DebugRenderer:DrawLine(areaPoints[#areaPoints], areaPoints[1], GREEN, GREEN)
  end

  local lines = {}

  local player = PlayerManager:GetLocalPlayer()
  if player.soldier and player.soldier.isAlive then
    local position = player.soldier.transform.trans
    table.insert(lines, 'Position: ' .. tostring(position))
    table.insert(lines, string.format('Chunk: (%d, %d)', position.x // 5, position.z // 5))
  end

  if levelScanner then
    table.insert(lines, 'Chunks completed: ' .. tostring(levelScanner:getChunksCompleted()))
    table.insert(lines, 'Chunks remaining: ' .. tostring(levelScanner:getChunksRemaining()))
    table.insert(lines, 'Runtime: ' .. formatTime(levelScanner:getRuntime()))
    table.insert(lines, 'Estimated time remaining: ' .. formatTime(levelScanner:getEstimatedTimeRemaining()))
  end

  local textY = TEXT_Y

  for _, v in pairs(lines) do
    DebugRenderer:DrawText2D(TEXT_X, textY, v, Vec4(0, 255, 0, 1), 1)
    textY = textY + TEXT_Y_STEP
  end

end)