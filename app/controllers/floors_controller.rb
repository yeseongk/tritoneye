class FloorsController < ApplicationController
  before_action :set_floor, only: [:show, :edit, :update, :destroy]

  def self.control
    redirect_to floors_url
  end

  # GET /floors
  # GET /floors.json
  def index
    @floors = Floor.all
    respond_to do |format|
      format.html {}
      format.js {render inline: "location.reload();" }
    end
  end

  # GET /floors/1
  # GET /floors/1.json
  def show
  end

  # GET /floors/new
  def new
    @floor = Floor.new
  end

  # GET /floors/1/edit
  def edit
  end

  # POST /floors
  # POST /floors.json
  def create
    @floor = Floor.new(floor_params)

    respond_to do |format|
      if @floor.save
        format.html { redirect_to @floor, notice: 'Floor was successfully created.' }
        format.json { render :show, status: :created, location: @floor }
      else
        format.html { render :new }
        format.json { render json: @floor.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /floors/1
  # PATCH/PUT /floors/1.json
  def update
    @div = 'floor_' + 
    respond_to do |format|
      if @floor.update(floor_params)
        format.html { redirect_to @floor, notice: 'Floor was successfully updated.' }
        format.json { render :show, status: :ok, location: @floor }
      else
        format.html { render :edit }
        format.json {  }
      end
    end
  end

  # DELETE /floors/1
  # DELETE /floors/1.json
  def destroy
    @floor.destroy
    respond_to do |format|
      format.html { redirect_to floors_url, notice: 'Floor was successfully destroyed.' }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_floor
      @floor = Floor.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def floor_params
      params.require(:floor).permit(:name, :capacity, :open_spots)
    end
end
