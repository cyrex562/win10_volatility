# Volatility
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details. 
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA 

"""
@author:       Andrew Case
@license:      GNU General Public License 2.0 or later
@contact:      atcuno@gmail.com
@organization: 
"""

import volatility.obj as obj
import volatility.plugins.linux.common as linux_common

class linux_check_idt(linux_common.AbstractLinuxCommand):
    """ Checks if the IDT has been altered """

    def calculate(self):
        """ 
        This works by walking the IDT table for the entries that Linux uses
        and verifies that each is a symbol in the kernel
        """
        linux_common.set_plugin_members(self)

        tblsz = 256

        sym_addrs = self.profile.get_all_addresses()

        # hw handlers + system call
        check_idxs = list(range(0, 20)) + [128]

        if self.profile.metadata.get('memory_model', '32bit') == "32bit":
            idt_type = "desc_struct"
        else:
            idt_type = "gate_struct64"

        # this is written as a list b/c there are supposdly kernels with per-CPU IDTs
        # but I haven't found one yet...
        addrs = [self.addr_space.profile.get_symbol("idt_table")]

        for tableaddr in addrs:

            table = obj.Object(theType = 'Array', offset = tableaddr, vm = self.addr_space, targetType = idt_type, count = tblsz)

            for i in check_idxs:

                ent = table[i]

                if not ent:
                    continue

                idt_addr = ent.Address

                if not idt_addr in sym_addrs:
                    yield(i, idt_addr, 1)
                else:
                    yield(i, idt_addr, 0)

    def render_text(self, outfd, data):

        self.table_header(outfd, [("Index", "[addr]"), ("Address", "[addrpad]"), ("Symbol", "<30")])

        for (i, idt_addr, hooked) in data:

            if hooked == 0:
                sym_name = self.profile.get_symbol_by_address("kernel", idt_addr)
            else:
                sym_name = "HOOKED"

            self.table_row(outfd, i, idt_addr, sym_name)




