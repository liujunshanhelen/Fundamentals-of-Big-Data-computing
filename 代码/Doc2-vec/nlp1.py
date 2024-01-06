import heapq
import os


class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


class HuffmanCoding:
    def __init__(self):
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}

    def make_frequency_dict(self, text):
        frequency = {}
        for char in text:
            if char not in frequency:
                frequency[char] = 0
            frequency[char] += 1
        return frequency

    def make_heap(self, frequency):
        for key in frequency:
            node = HuffmanNode(key, frequency[key])
            heapq.heappush(self.heap, node)

    def merge_nodes(self):
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)
            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(self.heap, merged)

    def make_codes_helper(self, root, current_code):
        if root is None:
            return
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper(root, current_code)

    def get_encoded_text(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if len(padded_encoded_text) % 8 != 0:
            print("Encoded text not padded properly")
            exit(0)
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i + 8]
            b.append(int(byte, 2))
        return b

    def compress(self, text):
        frequency = self.make_frequency_dict(text)
        self.make_heap(frequency)
        self.merge_nodes()
        self.make_codes()
        encoded_text = self.get_encoded_text(text)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        byte_array = self.get_byte_array(padded_encoded_text)
        return byte_array

    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-1 * extra_padding]
        return encoded_text

    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                character = self.reverse_mapping[current_code]
                decoded_text += character
                current_code = ""
        return decoded_text

    def decompress(self, byte_array):
        bit_string = ""
        for byte in byte_array:
            bits = bin(byte)[2:].rjust(8, '0')
            bit_string += bits
        encoded_text = self.remove_padding(bit_string)
        decompressed_text = self.decode_text(encoded_text)
        return decompressed_text


# 示例用法
text = "SELECT     /* LAS columns */  ls.ra, ls.dec,  ls.sourceID, ls.priOrSec, ls.frameSetID,  yapermag3, j_1apermag3, " \
         "hapermag3, kapermag3,  yapermag3err, j_1apermag3err, hapermag3err, kapermag3err,  yclass, j_1class, hclass, kclass, " \
         " yclassStat, j_1classStat, hclassStat, kclassStat  mergedclass, mergedclassStat,   pStar, pGalaxy, pNoise, pSaturated, " \
         " /* ErrBits */  ls.yErrBits, ls.j_1ErrBits, ls.hErrBits, ls.kErrBits,   ls.yppErrBits, ls.j_1ppErrBits, ls.hppErrBits," \
         " ls.kppErrBits,  /* x, y pixels  from detection tables*/ " \
         " ldy.x AS y_x, ldy.y AS y_y,  ldj.x AS j_x, ldj.y AS j_y,  ldh.x AS h_x, ldh.y AS h_y,  ldk.x AS k_x, ldk.y AS k_y, " \
         "  /* FIRST columns */  first.seqNo, first.ra AS ra_first, first.dec AS dec_first,  first.fint, first.fpeak, first.rms," \
         "  /* xmatch first columns */  LOF.distancemins as dr_first,   /* xmatch sdss columns */ " \
         " sdss.objid, LOS.distancemins as dr_sdss,  sdss.ra as ra_sdss, sdss.dec as dec_sdss,  sdss.psfmag_u, sdss.psfmag_g," \
         " sdss.psfmag_r,  sdss.psfmag_i, sdss.psfmag_z,  sdss.psfmagerr_u, sdss.psfmagerr_g, sdss.psfmagerr_r,  " \
         "sdss.psfmagerr_i, sdss.psfmagerr_z,  sdss.modelmag_u, sdss.modelmag_g, sdss.modelmag_r,  sdss.modelmag_i," \
         " sdss.modelmag_z,  sdss.modelmagerr_u, sdss.modelmagerr_g, sdss.modelmagerr_r,  sdss.modelmagerr_i, sdss.modelmagerr_z," \
         "  sdss.type, sdss.type_u, sdss.type_g,   sdss.type_r,sdss.type_i, sdss.type_z,  sdss.mode, sdss.flags, " \
         "  sdss.flags_u, sdss.flags_g, sdss.flags_r,   sdss.flags_i, sdss.flags_z,  /* SpecObj*/ Sso.z, Sso.zErr, Sso.zConf," \
         " Sso.zStatus, Sso.zWarning, Sso.specClass,  Sso.objTypeName  " \
         " /* INNER JOIN FIRST lasSourceXfirstSource with LasSource with */" \
         "  FROM    /* use the YJHK footprint */   LasYJHKSource AS ls " \
         " /* join conditions with mergelog table */  INNER JOIN Lasmergelog AS lml ON " \
         "    ls.framesetid = lml.framesetid    /* join conditions with source detection tables */ " \
         " INNER JOIN lasdetection AS ldy ON     ls.yseqnum = ldy.seqnum AND     lml.yenum = ldy.extNum AND  " \
         "   lml.ymfid = ldy.multiframeid   INNER JOIN lasdetection AS ldj ON     ls.j_1seqnum = ldj.seqnum " \
         " AND     lml.j_1enum = ldj.extNum AND     lml.j_1mfid = ldj.multiframeid    " \
         "  INNER JOIN lasdetection AS ldh ON     Lml.henum = Ldh.extNum AND" \
         "     lml.hmfid = Ldh.multiframeid and     ldh.seqnum = ls.hseqnum   " \
         "INNER JOIN lasdetection AS ldk ON     Lml.kenum = Ldk.extNum AND    " \
         " lml.kmfid = Ldk.multiframeid AND     ldk.seqnum = ls.kseqnum  INNER JOIN  " \
         "  /* Inner join between FIRST AND UKIDSS LAS */   (SELECT       sourceID, seqNo,      " \
         " masterObjID, slaveObjID, distancemins         FROM LasYJHKSource AS ls   " \
         " INNER JOIN LasSourceXfirstSource AS LxF       ON (LxF.masterObjID = ls.sourceID)  " \
         "  INNER JOIN FIRST..firstSource AS first       ON (LxF.slaveobjid = first.seqNo)    WHERE   " \
         "   /* resolved UKIDSS duplicate sources  */      ((ls.priOrSec = ls.frameSetID) OR (ls.priOrSec = 0)) AND    " \
         "  /* select within 1.5' */      (LxF.distanceMins < (1.5 / 60.0)) AND          LxF.distanceMins IN    " \
         "       /* select the nearest neighbour */     " \
         " (SELECT        MIN(distanceMins)      FROM      " \
         "  (SELECT              LXF.*            FROM              LasSourceXfirstSource AS LxF,          " \
         "    LasYJHKSource AS ls            WHERE              ((ls.priOrSec = ls.frameSetID) OR (ls.priOrSec = 0)) AND          " \
         "    LxF.masterObjID=ls.sourceID         ) AS LxF2      WHERE        LxF2.SlaveObjID=LxF.SlaveObjID)   ) AS LOF    ON  " \
         "    (ls.sourceid = LOF.sourceid)  INNER JOIN First..firstSource AS first    ON (first.seqNo = LOF.seqNo)  " \
         "  /* Left outer join with of UKIDSS with SDSS */ LEFT OUTER JOIN    (SELECT        sourceid, objid, distancemins  " \
         "   FROM       LasYJHKSource AS LS         INNER JOIN LasSourceXDR7PhotoObjAll AS LsXSp        " \
         "   ON LsXSp.masterObjID = Ls.sourceID         INNER JOIN BestDR7..PhotoObjAll AS Sp          " \
         " ON LsXSp.slaveobjid = Sp.objid     WHERE       /* set to 10.0 to decrease the drop out rate */  " \
         "     LsXSp.distanceMins<(10.0/60.0) AND       LsXSp.distanceMins IN        (SELECT MIN(T1.distanceMins) FROM             " \
         " LasSourceXDR7PhotoObj as T1            WHERE              T1.masterObjID = LsXSp.master"
huffman_coding = HuffmanCoding()
compressed_data = huffman_coding.compress(text)
decompressed_data = huffman_coding.decompress(compressed_data)

print("原始文本：", text)
print("压缩数据：", compressed_data)
print("解压缩后文本：", decompressed_data)
