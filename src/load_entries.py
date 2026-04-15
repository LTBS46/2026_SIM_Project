from readply import readply
from numpy import zeros, concatenate

def load_entries(entries: list[str]):
    v_entries = [None] * len(entries)
    t_entries = [None] * len(entries)
    
    v_off = 0
    tex_id = 0
    for __entry in entries:
        c_vert, c_tri = readply(__entry)
        c_vert2 = zeros((len(c_vert), 9))
        c_vert2[:, :8] = c_vert[:, :]
        c_vert2[:, 8] = tex_id
        c_tri += v_off
        v_off += len(c_vert)
        v_entries[tex_id] = c_vert2
        t_entries[tex_id] = c_tri
        tex_id += 1

    vertices = concatenate(v_entries)
    triangles = concatenate(t_entries)

    del c_vert, c_tri, c_vert2, v_off, tex_id, v_entries, t_entries

    return vertices, triangles