
uniform sampler2D uTextures[8];

in vec4 fColor;
in vec2 fTexCoords;
in float fTexID;

out vec4 color;

void main() {
	if(fTexID > -1){
		int id = int(fTexID);
		color = fColor * texture(uTextures[id], fTexCoords);
	}else{
		color = fColor;
	}
}
