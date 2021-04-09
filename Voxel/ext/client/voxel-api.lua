class('VoxelApi')

local BASE_URL = 'http://127.0.0.1:8000'
local POST_OPTIONS = HttpOptions({
  ['Content-Type'] = 'application/json'
})

function VoxelApi.static:getLevelsAsync(callback)
  Net:GetHTTPAsync(BASE_URL .. '/levels', callback)
end

function VoxelApi.static:getChunksAsync(levelId, callback)
  Net:GetHTTPAsync(BASE_URL .. '/levels/' .. string.format('%.0f', levelId) .. '/chunks', callback)
end

function VoxelApi.static:addChunkAsync(levelId, x, z, grid, type)

  local matrix = {}

  for i = 1, #grid do
    for j = 1, #grid[1] do
      for k = 1, #grid[1][1] do
        table.insert(matrix, grid[i][j][k])
      end
    end
  end

  local data = table.concat(matrix)
  --print(data)

  local data = {
    x = x,
    z = z, 
    width = #grid,
    height = #grid[1],
    depth = #grid[1][1],
    data = data,
    type = type
  }

  print('Url: ' .. BASE_URL .. '/levels/' .. string.format('%.0f', levelId) .. '/chunks')

  Net:PostHTTPAsync(BASE_URL .. '/levels/' .. string.format('%.0f', levelId) .. '/chunks', json.encode(data), POST_OPTIONS, function(response) 
    print(response)
  end)

end