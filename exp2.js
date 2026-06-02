let CPM = require("./artistoo-master/build/artistoo-cjs.js");
let fs = require('fs')
let path = require('path')

let GRID_WIDTH = 86
let GRID_HEIGHT = 86
let NUMBER_OF_CELLS = 20
let FINISH_ZONE = [[39,49],[72,82]]

//below is read from config file
let INIT_CHEMOKINE
let POOP_FACTOR
let DISSIPATION_FACTOR
let MAX_EAT
let NUMBER_OF_STEPS
let LAMBDA_CHEMOKINE
let config

function readConfig() {
	file_path = process.argv[2]

	config = JSON.parse(fs.readFileSync(file_path, {encoding: 'utf-8'}))
}

function setGlobals(){
	INIT_CHEMOKINE = config.globals.init_chemokine
	POOP_FACTOR = config.globals.poop_factor
	DISSIPATION_FACTOR = config.globals.dissipation_factor
	MAX_EAT = config.globals.max_eat
	NUMBER_OF_STEPS = config.simsettings.RUNTIME
	LAMBDA_CHEMOKINE = config.globals.lambda_chemokine
}

readConfig()
setGlobals()

// Initialize simulation for html
let sim, meter, borderConstraint
const walls = createMediumMaze();
const finish = createFinish()
const neighbourObject = {}

function initialize(){
	let custommethods = {
		initializeGrid : initializeGrid,
        postMCSListener : postMCSListener,
		drawBelow: drawBelow,
	}

	console.log(NUMBER_OF_CELLS)
	console.log(NUMBER_OF_STEPS)

    sim = new CPM.Simulation( config, custommethods )
    sim.g = new CPM.Grid2D([sim.C.extents[0],sim.C.extents[1]], config.conf.torus, "Float32")
    borderConstraint = sim.C.getConstraint("BorderConstraint")
    initializeNeighbourObject(sim.g)
    sim.g.diffusion = diffusion
    sim.g.neighNeumanni = neighNeumanni

	// Initial chemokine value for all cells in grid
	for (let x = 0; x < GRID_WIDTH; x++) {
		for (let y = 0; y < GRID_HEIGHT; y++) {
			if (isWallCoordinate(sim.g, [x, y])) continue;
			sim.g.setpix([x,y], INIT_CHEMOKINE)
		}
	}

    sim.C.add( new CPM.ChemotaxisConstraint( {
        LAMBDA_CH: LAMBDA_CHEMOKINE[0],
        CH_FIELD : sim.g }
    ) )

    // Manual BugFix
    let dH = function( sourcei, targeti, src_type, tgt_type ){
        let delta = this.field.pixti( targeti ) - this.field.pixti( sourcei ) 
        let lambdachem = this.cellParameter( "LAMBDA_CH", src_type )
        return -delta*lambdachem
    }
    sim.C.getConstraint("ChemotaxisConstraint", 0).deltaH = dH
    // End Manuel BugFix

	// meter = new FPSMeter({left:"auto", right:"5px"})
    // step()
    sim.run()
}

// function step(){
//     sim.step()
//     // meter.tick()
//     if( sim.conf["RUNTIME_BROWSER"] == "Inf" | sim.time+1 < sim.conf["RUNTIME_BROWSER"] ){
// 		requestAnimationFrame( step )
// 	}
// }

function initializeGrid() {
	if (!this.helpClasses['gm']) {
		this.addGridManipulator();
	}

	this.C.add(new CPM.BorderConstraint({
		BARRIER_VOXELS: walls
	}))

	let nrOfCells = NUMBER_OF_CELLS;
	for (let x = 18; x <= 33; x+=2) {
		for (let y = 1; y <= 16; y+=2) {
			if (nrOfCells <= 0) {
				break;
			}
			this.gm.seedCellAt(1, [x, y])
			nrOfCells--;
		}
	}
}

function postMCSListener(){
  let chemoSpawn = [50, 75]
  // Increase Chemokines
  this.g.setpix([50, 75], INIT_CHEMOKINE + this.g.pixt(chemoSpawn))

  // Chemokine diffusion 
	for( let i = 1 ; i <= 10 ; i ++ ){
		this.g.diffusion( this.C.conf["D"] )
	}
  
  // This is where he eats
  removeChemokines(this)

  // All my friends are dead
  finishCell(this, chemoSpawn)
  console.log(`CHEMOKINES\t${this.time}\t${sumChemokines(this.g)}`)
}

function removeChemokines(obj) {
	for (const pixels of Object.values(sim.C.getStat( CPM.PixelsByCell )).values()) {
		for (const location of pixels) {
			const old = obj.g.pixt(location)
			const eatAmount = Math.min(MAX_EAT, old)
			obj.g.setpix(location, old - eatAmount)
		}
	}
}

function finishCell(obj){
  for (const centroid of Object.values(sim.C.getStat( CPM.Centroids )).values()) {
      if (centroid[0] > FINISH_ZONE[0][0] && centroid[0] < FINISH_ZONE[0][1] &&
         centroid[1] > FINISH_ZONE[1][0] && centroid[1] < FINISH_ZONE[1][1]){
          let kill_id = obj.C.pixt([Math.round(centroid[0]), Math.round(centroid[1])])
          obj.gm.killCell(kill_id)
          console.log(`${obj.time}\t${kill_id}`);
          //Killed cell ${kill_id} at timestep ${obj.time}`);
      }
  }
}

function sumChemokines(grid) {
	let sum = 0;
	for (let x = 0; x < grid.extents[0]; x ++) {
		for (let y = 0; y < grid.extents[1]; y ++) {
			sum += grid.pixt([x, y]);
		}
	}
	return sum;
}

// Draws the pixels in BARRIER_VOXELS
function drawBelow() {
	if( !this.helpClasses["canvas"] ){ this.addCanvas() }
	this.Cim.drawField( this.g )
	this.Cim.drawCellBorders( -1, "000000" )
	this.Cim.drawPixelSet(walls, "AAAAAA");
  this.Cim.drawPixelSet(finish, "00FF00");
}

function drawFields(obj, cc, cc2, col = [0, 0, 255], col2 = [255, 0, 0] ){
	let maxval = 0;
	let maxval2 = 0;
	for( let i = 0 ; i < cc.extents[0] ; i ++ ){
		for( let j = 0 ; j < cc.extents[1] ; j ++ ){
			let p = Math.log(.1+cc.pixt([i,j]));
			let p2 = Math.log(.1+cc2.pixt([i,j]));

			if( maxval < p ){
				maxval = p;
			}

			if( maxval2 < p2 ){
				maxval2 = p2;
			}
		}
	}

	obj.getImageData();

	for( let i = 0 ; i < cc.extents[0] ; i ++ ){
		for( let j = 0 ; j < cc.extents[1] ; j ++ ){
			let alpha = Math.max(0, Math.min(1,(Math.log(.1+cc.pixt( [i,j] ))/maxval)))
			let alpha2 = Math.max(0, Math.min(1,(Math.log(.1+cc2.pixt( [i,j] ))/maxval2)))
			let baseCol = mixRGBA([...col, alpha], [...col2, alpha2])
			obj.col(rgbToHex(baseCol[0], baseCol[1], baseCol[2]));

			obj.pxfi([i,j], baseCol[3])
		}
	}
	obj.putImageData();
	obj.ctx.globalAlpha = 1;
}

function createFinish() {
  let finishPixels = []
  finishPixels = finishPixels.concat(getWallPixels({x: FINISH_ZONE[0][0], y: FINISH_ZONE[1][0]}, {x:FINISH_ZONE[0][1], y:FINISH_ZONE[1][1]}))
  return finishPixels
}

// Grid size: 528x100
function createEasyMaze() {
	let wallPixels = []

	wallPixels = wallPixels.concat(getWallPixels({x: 0, y: 31}, {x: 213, y: 31}))
	wallPixels = wallPixels.concat(getWallPixels({x: 0, y: 65}, {x: 213, y: 65}))
	wallPixels = wallPixels.concat(getWallPixels({x: 213, y: 0}, {x: 213, y: 30}))
	wallPixels = wallPixels.concat(getWallPixels({x: 213, y: 66}, {x: 213, y: 99}))
	wallPixels = wallPixels.concat(getWallPixels({x: 249, y: 32}, {x: 249, y: 64}))
	wallPixels = wallPixels.concat(getWallPixels({x: 249, y: 31}, {x: 527, y: 31}))
	wallPixels = wallPixels.concat(getWallPixels({x: 249, y: 65}, {x: 527, y: 65}))

	return wallPixels
}

// Grid size: 86x86
function createMediumMaze() {
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

// Expects two {x : Int, y: Int}, returns an array with pixels
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

// Expects two {x : Int, y: Int}, returns {smallestX: Int, largestX: Int, smallestY: Int, largestY: Int}
function inOrder(p1, p2) {
	return {
		smallestX: p1.x < p2.x ? p1.x : p2.x,
		largestX: p1.x >= p2.x ? p1.x : p2.x,
		smallestY: p1.y < p2.y ? p1.y : p2.y,
		largestY: p1.y >= p2.y ? p1.y : p2.y
	}
}

function initializeNeighbourObject(obj){
    if( ! obj._pixelsbuffer ) obj.pixelsBuffer();
    for( let i of obj.pixelsi() ){
		if (isWallIndex(obj, i)) {
			neighbourObject[i] = []
		} else {
	        neighbourObject[i] = neighboursi(obj, i, obj.torus)
		}
    }
}

function isWallIndex(grid, i){
	return walls.some(coord => coord[0] == grid.i2p(i)[0] && coord[1] == grid.i2p(i)[1])
}

function isWallCoordinate(grid, c){
	return isWallIndex(grid, grid.p2i(c))
}

function neighboursi( obj, i, torus ){
    // normal computation of neighbor indices (top left-middle-right, 
    // left, right, bottom left-middle-right)
    let t = i-1, l = i-obj.X_STEP, r = i+obj.X_STEP, b = i+1;
    
	function isBorder(j) {
		return isWallIndex(obj, j)
	}

    let result = []

	function add(cell, fallback, checkBorder = true) {
		if (isBorder(cell)) {
			result.push(fallback)
		} else {
			result.push(cell)
		}
	}

    // left border
    if( i < obj.extents[1]){
        if( torus[0] ){
            l += obj.extents[0] * obj.X_STEP;
            add(l, i)
        } else {
			result.push(i)
		}
    } else {
        add(l, i)
    }
    // right border
    if( i >= obj.X_STEP*( obj.extents[0] - 1 ) ){
        if( torus[0] ){
            r -= obj.extents[0] * obj.X_STEP;
            add(r, i)
        } else {
			result.push(i)
		}		
    } else {
        add(r, i)
    }
    // top border
    if( i % obj.X_STEP === 0 ){
        if( torus[1] ){
            t += obj.extents[1];
            add(t, i)
        } else {
			result.push(i)
		}
    } else {
        add(t, i)
    }
    // bottom border
    if( (i+1-obj.extents[1]) % obj.X_STEP === 0 ){
        if( torus[1] ){
            b -= obj.extents[1];
            add(b, i)
        } else {
			result.push(i)
		}
    } else {
        add(b, i)
    }

    return result
}


/** Perform a diffusion step on the grid, updating the values of all pixels
 * according to Fick's second law of diffusion.
 * @param {number} D diffusion coefficient
 * @see https://en.wikipedia.org/wiki/Diffusion#Fick's_law_and_equations
 * @see https://en.wikipedia.org/wiki/Discrete_Laplace_operator#Mesh_Laplacians
 * */
function diffusion( D ) {
    // For synchronous updating of the grid: compute updated values in a copy
    // of the current pixels
    if( ! this._pixelsbuffer ) this.pixelsBuffer();
    for( let i of this.pixelsi() ){
        if (borderConstraint.barriervoxels[i]) continue;
        // Diffusion: new value is current value + change.
        // the change is given by the diffusion coefficient D times the laplacian.
        this._pixelsbuffer[i] = this.pixti( i ) + D * this.laplaciani( i );
    }
    // swap the copy and the original
    [this._pixelsbuffer, this._pixels] = [this._pixels, this._pixelsbuffer];
}

// do not remove unused torus param!
function neighNeumanni( i, torus ){
    return neighbourObject[i]
}

initialize()
