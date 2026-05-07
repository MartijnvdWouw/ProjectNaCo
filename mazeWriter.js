const fs = require('fs');

STARTZONE = -3
UNREACHABLE = -2
WALL = -1
ENDZONE = 0

let minStartZoneDistance = 1000000000000;

function calculateDistances(width, height, wallPixels, startZone, endZone) {
    let distances = {}
    initStart(width, height, startZone, distances)
    initEnd(width, height, endZone, distances)
    initWalls(width, height, wallPixels, distances)

    calculate(width, height, endZone, distances)
    for (let x = 0; x < width; x ++) {
        for (let y = 0; y < height; y++) {
            if (distances[[x, y]] === undefined) distances[[x,y]] = UNREACHABLE
            if (distances[[x, y]] === STARTZONE) distances[[x,y]] = minStartZoneDistance
        }
    }
    return distances;
}

function calculate(width, height, endZone, distances) {
    let queue = [...endZone];

    while (queue.length > 0) {
        const pixel = queue.shift()
        const neighbours = getNeighbours(width, height, pixel)
        const curr = distances[pixel]
        if (curr === WALL) continue
        if (curr === undefined) throw new Error(`Pixel ${pixel} not present in distances!`)
        for (const nPixel of neighbours) {
            let nCurr = distances[nPixel]
            
            if (nCurr === STARTZONE && (curr + 1 < minStartZoneDistance)) {
                minStartZoneDistance = curr + 1
            }else if (nCurr === undefined  || (curr + 1 < nCurr)) {   
                distances[nPixel] = curr + 1
                queue.push(nPixel);
            }
        }
    }    
}

function _init(width, height, locations, defaultValue, result) {
    for (const [x, y] of locations) {
        if (x < 0 || x >= width || y < 0 || y >= height) {
            throw new Error(`Invalid coordinate [${x}, ${y}] expected coordinate 0 <= x < ${width} and 0 <= y < ${height}`);
        }
        result[[x, y]] = defaultValue;
    }
}

function initEnd(width, height, endZone, distances) {
    _init(width, height, endZone, ENDZONE, distances)
}

function initWalls(width, height, walls, distances) {
    _init(width, height, walls, WALL, distances)
}

function initStart(width, height, startZone, distances) {
    _init(width, height, startZone, STARTZONE, distances)
}

function getNeighbours(width, height, pixel) {
    let [x, y] = pixel;
    neighbours = []
    for (let i = x - 1; i <= x + 1; i ++) {
        for (let j = y - 1; j <= y + 1; j ++) {
            if (i >=0 && i < width && j >=0 && j < height && !(i == x && j == y)){
                neighbours.push([i, j])
            }
        }
    }
    return neighbours
}

function getVisualisationStr(width, height, distances) {
    let str = ""
    for (let i = 0; i < width; i ++) {
        for (let j = 0; j < height; j ++) {
            const val = distances[[j, i]]
            switch (val) {
                case WALL: 
                    str += "𝗪\t"
                    break
                case UNREACHABLE:
                    str += "❓\t"
                    break
                case ENDZONE:
                    str += "𝗘\t"
                    break
                default:
                    str += `${val}\t`
            }
        }
        str += "\n"
    }
    return str;
}

function getOutputStr(width, height, distances) {
    let str = `${width} ${height}\n`
    for (let i = 0; i < width; i ++) {
        for (let j = 0; j < height; j ++) {
            const val = distances[[i, j]]
            str += `${i} ${j} ${val}\n`
        }
    }
    return str;
}


function saveFile(filename, str) {
    fs.writeFile(`${filename}.txt`, str, (err) => {
        if (err) {
            console.error(err);
            return;
        }
    });
}

//copied from prototype.html
function getWallPixels(p1, p2) {
	let sorted = inOrder(p1, p2)

	let wallPixels = []
	for (let x = sorted.smallestX; x <= sorted.largestX; x++) {
		for (let y = sorted.smallestY; y <= sorted.largestY; y++) {
			wallPixels.push([x, y])
		}
	}
	return wallPixels
}

//copied from prototype.html
function inOrder(p1, p2) {
	return {
		smallestX: p1.x < p2.x ? p1.x : p2.x,
		largestX: p1.x >= p2.x ? p1.x : p2.x,
		smallestY: p1.y < p2.y ? p1.y : p2.y,
		largestY: p1.y >= p2.y ? p1.y : p2.y
	}
}

//copied from prototype.html
function _createMediumMaze() {
	let wallPixels = []

	wallPixels = wallPixels.concat(getWallPixels({x: 17, y: 0}, {x: 17, y: 17}))
	wallPixels = wallPixels.concat(getWallPixels({x: 17, y: 34}, {x: 17, y: 68}))
	wallPixels = wallPixels.concat(getWallPixels({x: 34, y: 34}, {x: 34, y: 51}))
	wallPixels = wallPixels.concat(getWallPixels({x: 51, y: 17}, {x: 51, y: 51}))
	wallPixels = wallPixels.concat(getWallPixels({x: 51, y: 68}, {x: 51, y: 85}))
	wallPixels = wallPixels.concat(getWallPixels({x: 68, y: 34}, {x: 68, y: 51}))
	wallPixels = wallPixels.concat(getWallPixels({x: 17, y: 17}, {x: 51, y: 17}))
	wallPixels = wallPixels.concat(getWallPixels({x: 68, y: 17}, {x: 85, y: 17}))
	wallPixels = wallPixels.concat(getWallPixels({x: 17, y: 51}, {x: 34, y: 51}))
	wallPixels = wallPixels.concat(getWallPixels({x: 68, y: 51}, {x: 85, y: 51}))
	wallPixels = wallPixels.concat(getWallPixels({x: 0, y: 68}, {x: 17, y: 68}))
	wallPixels = wallPixels.concat(getWallPixels({x: 34, y: 68}, {x: 68, y: 68}))

	// Borders
	wallPixels = wallPixels.concat(getWallPixels({x: 0, y: 0}, {x: 0, y: 85}))
	wallPixels = wallPixels.concat(getWallPixels({x: 0, y: 0}, {x: 85, y: 0}))
	wallPixels = wallPixels.concat(getWallPixels({x: 0, y: 85}, {x: 85, y: 85}))
	wallPixels = wallPixels.concat(getWallPixels({x: 85, y: 0}, {x: 85, y: 85}))

	return wallPixels
}

function _getMediumMazeEndZone() {
    let end = []
    for (let y = 69; y <= 85; y++) {
		end.push([50, y])
	}
    return end
}

function getMediumMazeParams() {
    return [86, 86, _createMediumMaze(), [], _getMediumMazeEndZone(), "mediumMaze"]
}

function run(width, height, wallPixels, startZone, endZone, filename, visualization=false) {
    const distances = calculateDistances(width, height, wallPixels, startZone, endZone)
    let str = visualization ? getVisualisationStr(width, height, distances) : getOutputStr(width, height, distances)
    saveFile(visualization ? `${filename}-viz`: filename, str)
}

//usage
run(...getMediumMazeParams())
//or for visualization
run(...getMediumMazeParams(), true)

//to run for easy maze, copy easy maze definitions from prototype.html (same things as for medium maze).
//to run this file, use node: node .\mazeWriter.js
