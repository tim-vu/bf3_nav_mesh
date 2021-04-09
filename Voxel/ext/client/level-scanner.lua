require('voxel-api')
require('voxelizer')
require('constants')
require('__shared/polygon')

class('LevelScanner')

local STEP_SIZE = Vec3(0.2, 0.24, 0.2)
local CHUNK_VOXEL_SIZE = 20

function LevelScanner:__init(levelId, area)

  self.levelId = levelId

  self.chunks = LevelScanner:_getChunksInArea(area)
  self.currentChunkIndex = 1

  print(string.format('Chunks: %d', #self.chunks))

  self.onUpdateEvent = nil
  self.voxelizer = nil
  self.startTime = nil
  self.chunkSizeX = STEP_SIZE.x * CHUNK_VOXEL_SIZE
  self.chunkSizeZ = STEP_SIZE.z * CHUNK_VOXEL_SIZE
end

local MAX = 99999999999999999999999
local MIN = -99999999999999999999999

function LevelScanner:_getChunksInArea(area)

  local minX = MAX
  local maxX = MIN

  local minZ = MAX
  local maxZ = MIN

  for _, v in pairs(area) do

    if v.x < minX then
      minX = v.x
    end

    if v.x > maxX then
      maxX = v.x
    end

    if v.y < minZ then
      minZ = v.y
    end

    if v.y > maxZ then
      maxZ = v.y
    end

  end

  local startChunkX = minX // self.chunkSizeX
  local startChunkZ = minZ // self.chunkSizeZ

  local endChunkX = maxX // self.chunkSizeX
  local endChunkZ = maxZ // self.chunkSizeZ

  local chunks = {}

  for i = startChunkX, endChunkX do
    for j = startChunkZ, endChunkZ do

      local corners = {}

      local min = Vec3(i * self.chunkSizeX, MIN_Y, j * self.chunkSizeZ)
      local max = Vec3(i * self.chunkSizeX + self.chunkSizeX, MAX_Y, j * self.chunkSizeZ + self.chunkSizeZ)
      local aabb = AxisAlignedBox(min, max)

      table.insert(corners, Vec2(aabb.min.x, aabb.min.z))
      table.insert(corners, Vec2(aabb.min.x, aabb.max.z))
      table.insert(corners, Vec2(aabb.max.x, aabb.min.z))
      table.insert(corners, Vec2(aabb.max.x, aabb.max.z))

      for _, v in pairs(corners) do

        if Polygon:isInside(area, v) then
          table.insert(chunks, {
            x = i,
            z = j,
            aabb = aabb
          })
          break
        end

      end

    end
  end

  return chunks

end

function LevelScanner:isRunning()
  return self._onUpdate ~= nil
end

function LevelScanner:getChunksCompleted()
  return self.currentChunkIndex - 1
end

function LevelScanner:getChunksRemaining()
  return #self.chunks - self.currentChunkIndex + 1
end

function LevelScanner:getRuntime()

  if not self.onUpdateEvent then
    return 0
  end

  return SharedUtils:GetTimeMS() - self.startTime
end

function LevelScanner:getEstimatedTimeRemaining()

  if not self.onUpdateEvent then
    return 0
  end

  local runtime = self:getRuntime()

  local chunksCompleted = self:getChunksCompleted()

  if chunksCompleted == 0 then
    return -1
  end

  local timePerChunk = runtime / chunksCompleted

  return timePerChunk * self:getChunksRemaining()

end

function LevelScanner:startScanning()

  if not self.onUpdateEvent then
    self.onUpdateEvent = Events:Subscribe('UpdateManager:Update', self, self._onUpdate)
    self.startTime = SharedUtils:GetTimeMS()
  end

end

function LevelScanner:_onUpdate(deltaTime, updatePass)

  if updatePass ~= UpdatePass.UpdatePass_PreSim then
    return
  end

  if not self.voxelizer then

    if self.currentChunkIndex > #self.chunks then
      print('Levelscanning done')
      self:stopScanning()
      return
    end

    local currentChunk = self.chunks[self.currentChunkIndex]

    self.voxelizer = Voxelizer(currentChunk.aabb, STEP_SIZE, CRITICAL_ANGLE[self.chunkType], RAYCASTS_PER_TICK)
  end

  local done = self.voxelizer:voxelize()

  if not done then
    return
  end

  local currentChunk = self.chunks[self.currentChunkIndex]

  print(string.format('Chunk done (x: %d, z: %d)', currentChunk.x, currentChunk.z))

  VoxelApi:addChunkAsync(self.levelId, currentChunk.x, currentChunk.z, self.voxelizer.grid, self.chunkType)

  self.voxelizer = nil
  self.currentChunkIndex = self.currentChunkIndex + 1

end

function LevelScanner:stopScanning()

  if self.onUpdateEvent then
    self.onUpdateEvent:Unsubscribe()
    self.onUpdateEvent = nil
  end

end