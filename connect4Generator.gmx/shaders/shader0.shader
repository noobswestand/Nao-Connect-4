//
// Simple passthrough vertex shader
//
attribute vec3 in_Position;                  // (x,y,z)
//attribute vec3 in_Normal;                  // (x,y,z)     unused in this shader.
attribute vec4 in_Colour;                    // (r,g,b,a)
attribute vec2 in_TextureCoord;              // (u,v)

varying vec2 v_vTexcoord;
varying vec4 v_vColour;

void main()
{
    vec4 object_space_pos = vec4( in_Position.x, in_Position.y, in_Position.z, 1.0);
    gl_Position = gm_Matrices[MATRIX_WORLD_VIEW_PROJECTION] * object_space_pos;
    
    v_vColour = in_Colour;
    v_vTexcoord = in_TextureCoord;
}

//######################_==_YOYO_SHADER_MARKER_==_######################@~//
// Simple passthrough fragment shader
//
varying vec2 v_vTexcoord;
varying vec4 v_vColour;

uniform int random[42];
vec2 float coords[42];
int count=0;

vec3 hsv2rgb(vec3 c) 
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
float point_distance(vec2 p0, vec2 p1){
    return pow(pow(p0.x-p1.x,2.0)+pow(p0.y-p1.y,2.0),0.5);
}

void main()
{
    vec4 org = texture2D(gm_BaseTexture, v_vTexcoord);
    vec3 black=vec3(0.0,0.0,0.0);
    vec3 col;
    
    gl_FragColor = v_vColour * org;
    
    if (org.rgb==black){
        for(int i=0;i<42;i+=1){
            if (point_distance(v_vTexcoord.xy,coords[i])<0.05){
                if (random[i]==0){
                    col= vec3(1.0, 1.0, 1.0);
                }
                if (random[i]==1){
                    col= vec3(1.0, 0.0, 0.0);
                }
                if (random[i]==2){
                    col= vec3(1.0, 1.0, 0.0);
                }
                gl_FragColor = v_vColour * vec4(col, org.a);
                //col= vec3(v_vTexcoord.x, 1.0, 1.0);
                //gl_FragColor = v_vColour * vec4(hsv2rgb(col), org.a);
            }
        }
    }
}
