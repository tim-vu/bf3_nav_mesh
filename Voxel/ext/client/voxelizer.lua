require('__shared/raycast')

class('Voxelizer')

local Axis = {
  ['x'] = 'x',
  ['y'] = 'y',
  ['z'] = 'z'
}

function Voxelizer.static:_getOtherAxes(axis)

  if Axis.x == axis then
    return {Axis.y, Axis.z}
  end

  if Axis.y == axis then
    return {Axis.x, Axis.z}
  end

  return {Axis.x, Axis.y}

end

function Voxelizer.static:_createMatrix(dimensions, valueFactory)

  local matrix = {}

  for i = 1, dimensions.x do
    matrix[i] = {}
    for j = 1, dimensions.y do
      matrix[i][j] = {}
      for k = 1, dimensions.z do
        matrix[i][j][k] = valueFactory(i, j, k)
      end
    end
  end

  return matrix
end

function Voxelizer.static:_isInside(aabb, vector)
  return vector.x >= aabb.min.x and vector.x <= aabb.max.x and vector.y >= aabb.min.y and vector.y <= aabb.max.y and vector.z >= aabb.min.z and vector.z <= aabb.max.z
end

function Voxelizer:__init(aabb, stepSize, criticalAngle, itersPerTick)

  self.aabb = aabb
  self.stepSize = stepSize
  self.itersPerTick = itersPerTick
  self.criticalAngle = criticalAngle

  local size = aabb.max - aabb.min

  self.steps = Vec3(
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
  print('Steps: ' .. tostring(self.steps))

  self.grid = Voxelizer:_createMatrix(Vec3(self.steps.x, self.steps.y, self.steps.z), function(i, j, k)
    return 0
  end)

  self.axesRemaining = {Axis.y, Axis.z, Axis.x}

  self.i = 1
  self.j = 1

  self.raycast = nil
end

function Voxelizer:createBoundingBoxMatrix()

  return Voxelizer:_createMatrix(Vec3(self.steps.x, self.steps.y, self.steps.z), function(i, j, k)

    local x = self.aabb.min.x + (i - 1) * self.stepSize.x
    local y = self.aabb.min.y + (j - 1) * self.stepSize.y
    local z = self.aabb.min.z + (k - 1) * self.stepSize.z

    local min = Vec3(x, y, z)
    local max = Vec3(x + self.stepSize.x, y + self.stepSize.y, z + self.stepSize.z)

    return AxisAlignedBox(min, max)

  end)

end

function Voxelizer:voxelize()

  if #self.axesRemaining == 0 then
    return true
  end

  local scanningAxis = self.axesRemaining[1]

  local rayCount = 0

  local axes = Voxelizer:_getOtherAxes(scanningAxis)
  local axis1 = axes[1]
  local axis2 = axes[2]

  while self.i <= self.steps[axis1] and rayCount < self.itersPerTick do

    while self.j <= self.steps[axis2] and rayCount < self.itersPerTick do

      local axis1_v = self.aabb.min[axis1] + (self.i - 1 + 0.5) * self.stepSize[axis1]
      local axis2_v = self.aabb.min[axis2] + (self.j - 1 + 0.5) * self.stepSize[axis2]

      local from = Vec3(0, 0, 0)
      from[axis1] = axis1_v
      from[axis2] = axis2_v
      from[scanningAxis] = self.aabb.max[scanningAxis]

      local to = Vec3(0, 0, 0)
      to[axis1] = axis1_v
      to[axis2] = axis2_v
      to[scanningAxis] = self.aabb.min[scanningAxis]

      if not self.raycast then
        self.raycast = Raycast(from, to, 0.01, self.itersPerTick)
      end

      local done, hits = self.raycast:performRaycast()

      if not done then
        return false
      else
        self.raycast = nil
      end

      for _, hit in pairs(hits) do

        local index = math.floor((hit.position[scanningAxis] - self.aabb.min[scanningAxis]) // self.stepSize[scanningAxis]) + 1

        local indices = {
          [scanningAxis] = index,
          [axis1] = self.i,
          [axis2] = self.j
        }

        local value

        if math.cos(self.criticalAngle) < hit.normal:Dot(Vec3.up) then
          value = 1
        else
          value = 2
        end

        local result, err pcall(function() 
        
          if self.grid[indices[Axis.x]][indices[Axis.y]][indices[Axis.z]] ~= 1 then
            self.grid[indices[Axis.x]][indices[Axis.y]][indices[Axis.z]] = value
          end
        end)

        if err then
          print(err)
          print('X: ' .. indices[Axis.x])
          print('Y: ' .. indices[Axis.y])
          print('Z: ' .. indices[Axis.z])

          print(string.format('Grid dim: (%d, %d, %d)', #self.grid, #self.grid[1], #self.grid[1][1]))
        end

      end

      self.j = self.j + 1
      rayCount = rayCount + 1
    end

    if self.j ~= self.steps[axis2] + 1 then
      return false
    end

    if self.i ~= self.steps[axis1] then
      self.j = 1
    end

    self.i = self.i + 1
  end

  if self.i == self.steps[axis1] + 1 and self.j == self.steps[axis2] + 1 then
    self.i = 1
    self.j = 1

    table.remove(self.axesRemaining, 1)

    if #self.axesRemaining == 0 then
      print('Done')
      return true
    end

    return false
  end

  return false

end